# Additional Installation Steps

## Cairo and Pandoc

The `chaos report` command relies on `cairo` and `pandoc` being present.

As well as installing the plugin by executing `pip install -U chaostoolkit-reporting`, you will also need to install `cairo` and `pandoc`.


### For Mac OS X
We recommend using the [Homebrew](https://brew.sh/) package manager to achieve this.

Once you have installed Homebrew, you can execute the following to install the third-party dependencies that the `chaos report` plugin uses:

```
$ brew install cairo pandoc
```


### For Debian/Ubuntu and Windows
You can install `pandoc` from the msi package installer or by using a .zip folder at `pandoc`'s [download page](https://github.com/jgm/pandoc/releases/tag/2.14.1)

As for `cairo`, this can be installed directly from the Cairo Graphics [download page](https://cairographics.org/download/)


## LaTeX

That's enough to produce HTML reports, but if you'd like to produce `.pdf` reports as well then you'll also need to install `latex` support. 


### For Mac OS X
The best way to install `latex` is to use Homebrew to grab `basictex`:

```
$ brew install basictex
```

Then use `ls /usr/local/Caskroom/basictex/` to see the actual directory the package resides in. Finally use the `open` command to run that Mac OS X package installer, for example:

```
$ open /usr/local/Caskroom/basictex/2017.0607/mactex-basictex-20170607.pkg
```

### For Debian/Ubuntu
We recommend using `sudo` to install the following packages:

```
$ sudo apt-get install texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    pdflatex
```

### For Windows
You can get `MiKTeX` through a system/command-line installer through the `MiXTeK` [download page](https://miktex.org/download) which contains the `LaTeX` package required

Once the installer has completed, you should then be able to produce `.pdf` reports as well.

***NOTES:***
- You may need start a new Terminal and then re-enable your Python virtual environment so that the `chaos report` command can find the `pdflatex` command it is looking for.

- If Python has been installed using `brew`, you may see the error:

  ```RuntimeError: Python is not installed as a framework. The Mac OS X backend will not be able to function correctly if Python is not installed as a framework.```

  In this case, run the following: `$ echo "backend: TkAgg" >> ~/.matplotlib/matplotlibrc`





