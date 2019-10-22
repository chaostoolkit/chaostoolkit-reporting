# Additional Installation Steps for Mac OS X

The `chaos report` command relies on `cairo` and `pandoc` being present.

As well as installing the plugin by executing `pip install -U chaostoolkit-reporting`, you will also need to install `cairo` and `pandoc`. We recommend using the [Homebrew](https://brew.sh/) package manager to achieve this.

Once you have installed Homebrew, you can execute the following to install the third-party dependencies that the `chaos report` plugin uses:

```
$ brew install cairo pandoc
```

That's enough to produce HTML reports, but if you'd like to produce `.pdf` reports as well then you'll also need to install `latex` support. The best way to install that is to use Homebrew to grab `basictex`:

```
$ brew cask install basictex
```

Then use `ls /usr/local/Caskroom/basictex/` to see the actual directory the package resides in. Finally use the `open` command to run that Mac OS X package installer, for example:

```
$ open /usr/local/Caskroom/basictex/2017.0607/mactex-basictex-20170607.pkg
```

Once the installer has completed, you should then be able to produce `.pdf` reports as well.

***NOTES:***
- You may need start a new Terminal and then re-enable your Python virtual environment so that the `chaos report` command can find the `pdflatex` command it is looking for.

- If Python has been installed using `brew`, you may see the error:

  ```RuntimeError: Python is not installed as a framework. The Mac OS X backend will not be able to function correctly if Python is not installed as a framework.```

  In this case, run the following: `$ echo "backend: TkAgg" >> ~/.matplotlib/matplotlibrc`

- If your terminal doesn't have the `LC_ALL` and `LANG` set, you may see the error:

  ```ValueError: unknown locale: UTF-8```

  In that case, configure the variables in your terminal configuration file. As example you can (use the definition that fits your workflow):

  ```
  export LC_ALL=en_US.UTF-8
  export LANG=en_US.UTF-8
  ```

  You will need to restart your terminal for your changes take effect.