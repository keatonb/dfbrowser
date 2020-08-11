# dfbrowser
Interactive plots for exploring and selecting points from DataFrames in a Jupyter notebook.  You must use the [ipympl](https://github.com/matplotlib/ipympl) backend with the notebook magic command `%matplotlib widget`  Simple as passing DataFrame `df` to a `dfbrowser` instance with

```python3
from dfbrowser import dfbrowser
browse = dfbrowser(df)
```

This will produce an interactive scatterplot of numeric column data from your DataFrame. Here's an example screenshot with random data:

![Example dfbrowser screenshot](https://github.com/keatonb/dfbrowser/blob/master/screenshot.png)

You can pick which columns to plot from the dropdown menus.  Click near points to select them.  The pandas Series associated with the selected row is passed to user defined function `funct` (either defined upon initialization or by setting the `dfbrowser.funct` parameter).  This function must be able to accept a pandas Series object as input (the "print" function is a sensible choice).  You can also access the currently selected index and row as `dfbrowser.selectedindex` and `dfbrowser.selectedrow`.

I use this tool to explore a large number of astronomical light curves for many stars, each of which has a number of numerical values associated with it (e.g., position on sky, average brightness, dominant timescale of variablility).  I use `dfbrowser` to see how these stars are distributed in different parameter spaces, and then I connect a function that displays the associated light curve (loaded from a column containing filenames usually) for any point I click on.

Raise an issue if you would like to see any other functionality.  I plan to let marker sizes and colors vary with third and fourth columns eventually.
