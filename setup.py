from distutils.core import setup


VERSION = '0.1.0'
if __name__ == "__main__":
    setup(install_requires=['distribute'],
          name="wd2epub",
          author="Serhiy Lysovenko",
          version=VERSION,
          license="GPLv3",
          packages=["wd2epub"],
          package_data={"wd2epub": ["fonts.zip", "core.zip"]},
          package_dir={"wd2epub": "."},
          url="http://")
