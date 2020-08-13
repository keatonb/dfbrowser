#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 13:16:10 2020

Quickly explore data stored in a pandas DataFrame in a Jupyter Notebook. Choose 
which numeric columns to plot in a scatter plot, and click on any point to 
retreive the associated row. Must use the ipympl backend with the notebook 
magic `%matplotlib widget`.

There are three ways to pass the selected row data to a different function:
     - pass on init with the funct argument
     - connect after initialization by setting dfbrowser.funct to the function
     - access currently selected index as dfbrowser.selectedindex or associated
     row as dfbrowser.selectedrow

Based on the matplotlib event_handling example code: data_browser.py at
https://matplotlib.org/2.0.0/examples/event_handling/data_browser.html

Uses ipywidgets and ipympl for interaction in a Jupyter notebook. Users must 
enable the associated Jupyter notebook extension following
https://ipywidgets.readthedocs.io/en/latest/user_install.html
and https://github.com/matplotlib/ipympl , andthe ipympl backend must be 
enabled with the magic Jupyter command `%matplotlib widget`.

Future improvements will allow users to color and size the scatter plot points
by additional column values.

Distinguish clicks with drag motions from ImportanceOfBeingErnest
https://stackoverflow.com/a/48452190

@author: keatonb
"""

from __future__ import division, print_function
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from matplotlib.backend_bases import NavigationToolbar2

class dfbrowser(object):
    """
    Interactive scatter plot of selectable pandas DataFrame values.
    """
    
    def __init__(self,df,columns=None,figsize=(5,5),funct=None,show=True,**kwargs):
        """
        Parameters
        ----------
        df : pandas dataframe
            Contains data to plot in columns.
        columns : list of strings
            Column names to plot (must be numeric). Default is all numeric df columns.
        figsize : tuple
            Figure width, height in inches. The default is (5,5).
        funct : function, optional
            Function to send DataFrame rows to upon selection. The default is None.
        show : bool, optional
            Whether to display figure upon initialization. The default is True.
        **kwargs : kwargs
            Get passed to scatterplot function call
        """
        self.df = df
        plt.ioff()#don't display
        self.fig, self.ax = plt.subplots(1,1,figsize=figsize,constrained_layout=True)
        self.funct = funct
        
        #Include all numeric columns if columns not specified
        self.columns = columns
        if self.columns is None:
            self.columns = []
            for col in self.df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    self.columns.append(col)
        
        self._init_widgets()
        
        #Make initial scatter plot
        #make marker size 1 if not otherwise specified
        if 's' not in kwargs.keys():
            kwargs['s'] = 1
        self.scatter = self.ax.scatter(self.df[self._xvar.value],self.df[self._yvar.value],**kwargs)
        #Keep track and mark last clicked point (by df index)
        #following https://matplotlib.org/2.0.0/examples/event_handling/data_browser.html
        self.selectedindex = None
        self.selectedrow = None
        self.ax.set_title('selected index: none')
        self.selected, = self.ax.plot([self.df[self._xvar.value][0],self.df[self._yvar.value][0]], 'o', ms=12, alpha=0.4,
                                 color='yellow', visible=False)
        #Show and update plot
        if show:
            display(self.show())
        self._replot()
        #Reconnect home toolbar button to my own function
        plt.get_current_fig_manager().toolbar.home = self._replot
        
        #Connect click events, check that it's not a drag event
        #https://stackoverflow.com/a/48452190
        self._press= False
        self._move = False
        self.fig.canvas.mpl_connect('button_press_event', self._onpress)
        self.fig.canvas.mpl_connect('button_release_event', self._onrelease)
        self.fig.canvas.mpl_connect('motion_notify_event', self._onmove)
        
    def _init_widgets(self):
        self._xvar = widgets.Dropdown(options=self.columns,
                                      description='x var:',
                                      value=self.columns[0]
                                      )
        self._xvar.observe(self._changevar)
        self._yvar = widgets.Dropdown(options=self.columns,
                                      description='y var:',
                                      value=self.columns[1]
                                      )
        self._yvar.observe(self._changevar)
        
        self._xreverse = widgets.Checkbox(
            value=False,
            description='reverse'
        )
        self._xreverse.observe(self._flipaxis)
        self._yreverse = widgets.Checkbox(
            value=False,
            description='reverse'
        )
        self._yreverse.observe(self._flipaxis)
        
        #Make a widget to capture function output:
        self.output = widgets.Output()
        
    def _changevar(self,event):
        if event["name"] == 'value':
            self._replot()
            
    def _flipaxis(self,event=None):
        flip = False
        if event is None:
            flip = True
        elif event["name"] == 'value':
            flip = True
        if flip:
            if self._xreverse.value == (np.diff(self.ax.get_xlim())[0] > 0):
                self.ax.invert_xaxis()
            if self._yreverse.value == (np.diff(self.ax.get_ylim())[0] > 0):
                self.ax.invert_yaxis()
            self.fig.canvas.draw()
    
    def _replot(self,pad=0.02):
        #Plot new points
        self.scatter.set_offsets(self.df[[self._xvar.value,self._yvar.value]])
        
        #change plot limits
        minx = np.nanmin(self.df[self._xvar.value])
        maxx = np.nanmax(self.df[self._xvar.value])
        xpad = (maxx-minx)*pad
        newxlim = np.array([minx-xpad,maxx+xpad])
        
        self.ax.set_xlim(newxlim)
        self.ax.set_xlabel(self._xvar.value)
        
        miny = np.nanmin(self.df[self._yvar.value])
        maxy = np.nanmax(self.df[self._yvar.value])
        ypad = (maxy-miny)*pad
        newylim = np.array([miny-ypad,maxy+ypad])
        
        self.ax.set_ylim(newylim)
        self.ax.set_ylabel(self._yvar.value)
        
        #flip axes if selected
        self._flipaxis()
        
        #update marker for selected point
        self._updatemarker()
        
    #Click event action
    def _onclick(self,event):
        
        if event.xdata is not None:
            #Compute distace from clicks to points
            #Adjusting for different x and y scales
            bbox = self.ax.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
            axwidth, axheight = bbox.width, bbox.height
            xspan = np.abs(np.diff(self.ax.get_xlim())[0])
            yspan = np.abs(np.diff(self.ax.get_ylim())[0])
            xscale = xspan/axwidth
            yscale = yspan/axheight
            
            #Select nearest data point
            xdiff = (self.df[self._xvar.value] - event.xdata)/xscale
            ydiff = (self.df[self._yvar.value] - event.ydata)/yscale
            distance = np.sqrt(xdiff**2. + ydiff**2.)
            
            #Make this available
            self.selectedindex = np.nanargmin(distance)
            self.selectedrow = self.df.iloc[self.selectedindex]
            self._updatemarker()
            
            #Pass to function
            self._passtofunct()
                    
    def _passtofunct(self):
        with self.output:
            if self.funct is not None:
                try:
                    self.funct(self.selectedrow)
                except:
                    raise Exception("Passing DataFrame row to user function failed.")
    
    def clearoutput(self):
        """Clear output widget text
        """
        self.output.clear_output()
    
    def _updatemarker(self):
        #https://matplotlib.org/2.0.0/examples/event_handling/data_browser.html
        if self.selectedindex is None:
            return
        
        self.ax.set_title('selected index: '+str(self.selectedindex))
        
        self.selected.set_visible(True)
        self.selected.set_data(self.df[self._xvar.value].iloc[self.selectedindex],
                               self.df[self._yvar.value].iloc[self.selectedindex])
        
        self.fig.canvas.draw()
    
    #This stuff distinguishes clicks from drags
    #https://stackoverflow.com/a/48452190
    def _onpress(self,event):
        print('press')
        self._press=True
    def _onmove(self,event):
        print('move')
        if self._press:
            self._move=True
    def _onrelease(self,event):
        print('release')
        if self._press and not self._move:
            self._onclick(event)
        self._press=False; self._move=False
        
        
    def show(self):
        show = widgets.VBox([widgets.HBox([self._xvar,self._xreverse]),
                             widgets.HBox([self._yvar,self._yreverse]),
                             self.fig.canvas,self.output])
        return show
        
        
        
        