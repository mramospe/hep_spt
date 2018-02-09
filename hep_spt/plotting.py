'''
Provide some useful functions to plot with matplotlib.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Local
from hep_spt import __project_path__
from hep_spt.math_aux import lcm
from hep_spt.stats import poisson_fu, poisson_llu, sw2_u

# Python
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import math, os
from cycler import cycler


__all__ = [
    'available_styles',
    'centers_from_edges',
    'corr_hist2d',
    'errorbar_hist',
    'opt_fig_div',
    'path_to_styles',
    'process_range',
    'profile',
    'pull',
    'samples_cycler',
    'set_style',
    'text_in_rectangles'
    ]

# Path to the directory containing the styles
__path_to_styles__ = os.path.join(__project_path__, 'mpl')


def available_styles():
    '''
    :returns: list with the names of the available styles within this package.
    :rtype: list(str)
    '''
    available_styles = list(map(lambda s: s[:s.find('.mplstyle')],
                                os.listdir(__path_to_styles__)))
    return available_styles


def centers_from_edges( edges ):
    '''
    :param edges: edges of a histogram.
    :type edges: numpy.ndarray
    :returns: centers of the histogram.
    :rtype: numpy.ndarray
    '''
    return (edges[1:] + edges[:-1])/2.


def corr_hist2d( ax, matrix, titles, frmt = '{:.2f}', vmin = None, vmax = None ):
    '''
    Plot a given correlation matrix in the given axes.

    :param ax: where to draw the histogram.
    :type ax: matplotlib.axes.Axes
    :param matrix: correlation matrix.
    :type matrix: numpy.ndarray
    :param titles: name of the variables being represented.
    :type titles: collection(str)
    :param frmt: format to display the correlation value in each bin. By \
    default it is assumed that the values go between :math:`[0, 1]`, so \
    three significant figures are considered. If "frmt" is None, then \
    no text is displayed in the bins.
    :type frmt: str
    :param vmin: minimum value to represent in the histogram.
    :type vmin: float
    :param vmax: maximum value to represent in the histogram.
    :type vmax: float
    '''
    edges = np.linspace(0, len(titles), len(titles) + 1)

    centers = centers_from_edges(edges)

    x, y = np.meshgrid(centers, centers)

    x = x.reshape(x.size)
    y = y.reshape(y.size)
    c = matrix.reshape(matrix.size)

    vmin = vmin or c.min()
    vmax = vmax or c.max()

    ax.hist2d(x, y, (edges, edges), weights=c, vmin=vmin, vmax=vmax)

    # Modify the ticks to display the variable names
    for i, a in enumerate((ax.xaxis, ax.yaxis)):

        a.set_major_formatter(ticker.NullFormatter())
        a.set_minor_formatter(ticker.FixedFormatter(titles))

        a.set_major_locator(ticker.FixedLocator(edges))
        a.set_minor_locator(ticker.FixedLocator(centers))

        for tick in a.get_minor_ticks():
            tick.tick1line.set_markersize(0)
            tick.tick2line.set_markersize(0)
            tick.label1.set_rotation(45)

            if i == 0:
                tick.label1.set_ha('right')
            else:
                tick.label1.set_va('top')

    # Annotate the value of the correlation
    if frmt is not None:
        for ix, iy, ic in zip(x, y, c):
            ax.annotate(frmt.format(ic), xy=(ix, iy), ha='center', va='center')

    # Draw the grid
    ax.grid()


def errorbar_hist( arr, bins = 20, rg = None, wgts = None, norm = False, uncert = None ):
    '''
    Calculate the values needed to create an error bar histogram.

    :param arr: input array of data to process.
    :param bins: see :func:`numpy.histogram`.
    :type bins: int or sequence of scalars or str
    :param rg: range to process in the input array.
    :type rg: tuple(float, float)
    :param wgts: possible weights for the histogram.
    :type wgts: collection(value-type)
    :param norm: if True, normalize the histogram. If it is set to a number, \
    the histogram is normalized and multiplied by that number.
    :type norm: bool, int or float
    :param uncert: type of uncertainties to consider. If None, frequentist \
    poissonian uncertainties will be considered for non-weighted data, while \
    the sum of squares of weights is used for weighted data. The possibilities \
    are: \
    - "freq": frequentist uncertainties. \
    - "dll": uncertainty based on the difference on the logarithm of \
    likelihood. \
    - "sw2": sum of square of weights. In case of non-weighted data, the \
    uncertainties will be equal to the square root of the entries in the bin. \
    A warning is raised if one tries to use "freq" or "dll" on weighted data.
    :type uncert: str or None
    :returns: values, edges, the spacing between bins in X the Y errors. \
    In the non-weighted case, errors in Y are returned as two arrays, with the \
    lower and upper uncertainties.
    :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray

    .. seealso:: :func:`hep_spt.stats.poisson_fu`, :func:`hep_spt.stats.poisson_llu`
    '''
    if uncert not in (None, 'freq', 'dll', 'sw2'):
        raise ValueError('Unknown uncertainty type "{}"'.format(uncert))

    if wgts is not None:

        if uncert in ('freq', 'dll'):
            warnings.warn('Uncertainties of type "{}" can not be used on '\
                          'weighted data'.format(uncert))

        values, edges = np.histogram(arr, bins, weights = wgts)

        # Use sum of the square of weights to calculate the error
        ey = sw2_u(arr, bins, rg, wgts)

    else:
        # By default use frequentist poissonian errors
        uncert = uncert or 'freq'

        # Use the poissonian errors
        values, edges = np.histogram(arr, bins, rg, weights = wgts)

        if uncert == 'freq':
            ey = poisson_fu(values)
        elif uncert == 'dll':
            ey = poisson_llu(values)
        else:
            ey = sw2_u(arr, bins, rg, wgts)

        # For compatibility with matplotlib.pyplot.errorbar
        ey = ey.T

    ex = (edges[1:] - edges[:-1])/2.

    if norm:

        s = float(values.sum())/norm

        if s != 0:
            values = values/s
            ey = ey/s
        else:
            ey *= np.finfo(ey.dtype).max

    return values, edges, ex, ey


def opt_fig_div( naxes ):
    '''
    Get the optimal figure division for a given number of axes, where
    all the axes have the same dimensions.

    :param naxes: number of axes to plot in the figure.
    :type naxes: int
    :returns: number of rows and columns of axes to draw.
    :rtype: int, int
    '''
    nstsq = int(round(math.sqrt(naxes)))

    if nstsq**2 > naxes:
        nx = nstsq
        ny = nstsq
    else:
        nx = nstsq
        ny = nstsq
        while nx*ny < naxes:
            ny += 1

    return nx, ny


def path_to_styles():
    '''
    :returns: path to the directory containing the styles.
    :rtype: str
    '''
    return __path_to_styles__


def process_range( arr, rg = None ):
    '''
    Process the given range, determining the minimum and maximum
    values for a 1D histogram.

    :param arr: array of data.
    :type arr: numpy.ndarray
    :param rg: range of the histogram. It must contain tuple(min, max), \
    where "min" and "max" can be either floats (1D case) or collections \
    (ND case).
    :type rg: tuple or None
    :returns: minimum and maximum values.
    :rtype: float, float
    '''
    if rg is not None:
        vmin, vmax = rg
    else:
        amax = arr.max(axis = 0)
        vmin = arr.min(axis = 0)
        vmax = np.nextafter(amax, np.infty)

    return vmin, vmax


def profile( x, y, bins = 20, rg = None ):
    '''
    Calculate the profile from a 2D data sample. It corresponds to the mean of
    the values in "y" for each bin in "x".

    :param x: values to consider for the binning.
    :type x: collection(value-type)
    :param y: values to calculate the mean with.
    :type y: collection(value-type)
    :param bins: see :func:`numpy.histogram`.
    :type bins: int or sequence of scalars or str
    :param rg: range to process in the input array.
    :type rg: tuple(float, float)
    :returns: profile in "y".
    :rtype: numpy.ndarray
    '''
    _, edges = np.histogram(x, bins, rg)

    dig = np.digitize(x, edges)

    prof = np.array([
        y[dig == i].mean() for i in range(1, len(edges))
    ])

    return prof


def pull( vals, err, ref ):
    '''
    Get the pull with the associated errors for a given set of values and a
    reference. Considering, :math:`v` as the experimental value and :math:`r`
    as the rerference, the definition of this quantity is :math:`(v - r)/\sigma`
    in case symmetric errors are provided. In the case of asymmetric errors the
    definition is:

    .. math::
       \\text{pull}
       =
       \Biggl \lbrace
       {
       (v - r)/\sigma_{low},\\text{ if } v - r \geq 0
       \\atop
       (v - r)/\sigma_{up}\\text{ otherwise }
       }

    In the latter case, the errors are computed in such a way that the closer to
    the reference is equal to 1 and the other is scaled accordingly, so if
    :math:`v - r > 0`, then :math:`\sigma^{pull}_{low} = 1` and
    :math:`\sigma^{pull}_{up} = \sigma_{up}/\sigma_{low}`.

    :param vals: values to compare with.
    :type vals: array-like
    :param err: array of errors. Both symmetric and asymmetric errors \
    can be provided. In the latter case, they must be provided as a \
    (2, n) array.
    :type err: array-like
    :param ref: reference to follow.
    :type ref: array-like
    :returns: pull of the values with respect to the reference and \
    associated errors. In case asymmetric errors have been provided, \
    the returning array has shape (2, n).
    :rtype: array-like, array-like
    '''
    pull = vals - ref

    perr = np.ones_like(err)

    if len(err.shape) == 1:
        # Symmetric errors
        pull /= err

    elif len(err.shape) == 2:
        # Asymmetric errors

        up = (pull >= 0)
        lw = (pull < 0)

        el, eu = err

        pull[up] /= el[up]
        pull[lw] /= eu[lw]

        perr_l, perr_u = perr

        perr_l[lw] = (el[lw]/eu[lw])
        perr_u[up] = (eu[up]/el[up])
    else:
        raise TypeError('The error array must have shape (2, n) or (n,)')

    return pull, perr


def samples_cycler( smps, *args, **kwargs ):
    '''
    Often, one wants to plot several samples with different matplotlib
    styles. This function allows to create a cycler.cycler object
    to loop over the given samples, where the "label" key is filled
    with the values from "smps".

    :param smps: list of names for the samples.
    :type smps: collection(str)
    :param args: position argument to cycler.cycler.
    :type args: tuple
    :param kwargs: keyword arguments to cycler.cycler.
    :type kwargs: dict
    :returns: cycler object with the styles for each sample.
    :rtype: cycler.cycler
    '''
    cyc = cycler(*args, **kwargs)

    ns = len(smps)
    nc = len(cyc)

    if ns > nc:

        warnings.warn('Not enough plotting styles in cycler, '\
                      'some samples might have the same style.')

        l = math_aux.lcm(ns, nc)

        re_cyc = (l*cyc)[:ns]
    else:
        re_cyc = cyc[:ns]

    return re_cyc + cycler(label = smps)


def set_style( *args ):
    '''
    Set the style for matplotlib to one within this project. Available styles
    are:

    * singleplot: designed to create a single figure.
    * multiplot: to make subplots. Labels and titles are smaller than in \
    "singleplot", although lines and markers maintain their sizes.

    By default the "singleplot" style is set.

    :param args: styles to load.
    :type args: tuple
    '''
    args = list(args)
    if len(args) == 0:
        # The default style is always set
        args = ['default', 'singleplot']
    elif 'default' not in args:
        args.insert(0, 'default')

    avsty = available_styles()

    sty_args = []
    for s in args:
        if s not in avsty:
            warnings.warn('Unknown style "{}", will not be loaded'.format(style))
        else:
            sty_args.append(os.path.join(__path_to_styles__, '{}.mplstyle'.format(s)))

    plt.style.use(sty_args)


def text_in_rectangles( ax, recs, txt, **kwargs ):
    '''
    Write text inside matplotlib.patches.Rectangle instances.

    :param ax: axes where the rectangles are being drawn.
    :type ax: matplotlib.axes.Axes
    :param recs: set of rectangles to work with.
    :type recs: collection(matplotlib.patches.Rectangle)
    :param txt: text to fill with in each rectangle.
    :type txt: collection(str)
    :param kwargs: any other argument to matplotlib.axes.Axes.annotate.
    :type kwargs: dict
    '''
    for r, t in zip(recs, txt):
        x, y = r.get_xy()

        cx = x + r.get_width()/2.
        cy = y + r.get_height()/2.

        ax.annotate(t, (cx, cy), **kwargs)