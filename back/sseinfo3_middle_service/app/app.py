import sys

from initialization import create_app

app = create_app()

if __name__ == "__main__":
    # print(app.url_map)
    # app.run()
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back


    aa = currentframe.__code__.co_filename
    import os

    bb = os.path.normcase(currentframe.__code__.co_filename)


    print()