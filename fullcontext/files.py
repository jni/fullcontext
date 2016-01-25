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
