####
##
##
#
"""
module description
"""

# import os
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
@app.get("/{param}")
async def docroot(param=""):
    """ default route """
    return "And They Have a Plan"


def main():
    """Main proc"""


if __name__ == "__main__":
    main()
