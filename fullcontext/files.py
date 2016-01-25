import os
from urllib.request import urlopen
import tempfile
from contextlib import contextmanager


@contextmanager
def temporary_file(suffix=''):
    """Yield a writeable temporary filename that is deleted on context exit.

    Parameters
    ----------
    suffix : string, optional
        The suffix for the file.
    """
    tempfile_stream = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tempfile = tempfile_stream.name
    tempfile_stream.close()
    yield tempfile
    os.remove(tempfile)


@contextmanager
def download(url : str, **kwargs) -> str:
    """Download remote file and yield the local filename.

    This context manager is useful to load a remote filename using a library
    that only supports opening local files.

    Parameters
    ----------
    url : string
        The remote URL of the file you want to open.
    kwargs :
        Additional arguments to pass on to `tempfile.NamedTemporaryFile`.
        The `suffix` argument cannot be overridden and always matches the
        extension on the URL.

    Yields
    ------
    filename : string

    Examples
    --------
    >>> with download('http://www.linfo.org/bsdlicense.html') as fn:
    ...     assert fn.endswith('html')
    ...     contents = ''.join(open(fn).readlines())
    ...     # check file contains </body> and </html> closing tags, in order
    ...     assert -1 < contents.find('</body>') < contents.find('</html>')
    """
    base_filename, ext = os.path.splitext(url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext, **kwargs) as f:
        remote = urlopen(url)
        f.write(remote.read())
    try:
        yield f.name
    finally:
        os.remove(f.name)


# file-or-url code below adapted from scikit-image under the BSD license.
URL_REGEX = re.compile(r'http://|https://|ftp://|file://|file:\\')


def is_url(filename):
    """Return True if string is an http or ftp path."""
    return (isinstance(filename, six.string_types) and
            URL_REGEX.match(filename) is not None)


@contextmanager
def file_or_url(resource_name):
    """Yield name of file from the given resource (i.e. file or url)."""
    if is_url(resource_name):
        _, ext = os.path.splitext(resource_name)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f:
            u = urlopen(resource_name)
            f.write(u.read())
        try:
            yield f.name
        finally:
            os.remove(f.name)
    else:
        yield resource_name
