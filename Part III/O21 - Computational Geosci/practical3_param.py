# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown] id="jnf7uNVY_S-n"
# # Practical 3: Model parameterization
#
# The goal of this practical is to introduce you to the concept of model parameterization, or how we mathematically describe models that are going to be used to represent structure or processes. This includes how we might form a continuum from a discrete set of parameters; for example, given a regular or irregular set of points, what choice of interpolation function might we use to fully describe the model?

# %% id="9nIiHpzU_S-r"
# Here, we just import some functions and modules that are used in the practical
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline


# This bit of code works out the coefficients for natural cubic splines given
# a set of points x, y
def CubicNatural(x, y):
    m = x.size  # m is the number of data points
    n = m - 1
    a = np.zeros(m)
    b = np.zeros(n)
    c = np.zeros(m)
    d = np.zeros(n)
    for i in range(m):
        a[i] = y[i]
    h = np.zeros(n)
    for i in range(n):
        h[i] = x[i + 1] - x[i]
    u = np.zeros(n)
    u[0] = 0
    for i in range(1, n):
        u[i] = 3 * (a[i + 1] - a[i]) / h[i] - 3 * (a[i] - a[i - 1]) / h[i - 1]
    s = np.zeros(m)
    z = np.zeros(m)
    t = np.zeros(n)
    s[0] = 1
    z[0] = 0
    t[0] = 0
    for i in range(1, n):
        s[i] = 2 * (x[i + 1] - x[i - 1]) - h[i - 1] * t[i - 1]
        t[i] = h[i] / s[i]
        z[i] = (u[i] - h[i - 1] * z[i - 1]) / s[i]
    s[m - 1] = 1
    z[m - 1] = 0
    c[m - 1] = 0
    for i in np.flip(np.arange(n)):
        c[i] = z[i] - t[i] * c[i + 1]
        b[i] = (a[i + 1] - a[i]) / h[i] - h[i] * (c[i + 1] + 2 * c[i]) / 3
        d[i] = (c[i + 1] - c[i]) / (3 * h[i])
    return a, b, c, d


# This bit of code discretely samples the spline curve at point w.
def CubicNaturalEval(w, x, coeff):
    m = x.size
    if w < x[0] or w > x[m - 1]:
        print("error: spline evaluated outside its domain")
        return
    n = m - 1
    p = 0
    for i in range(n):
        if w <= x[i + 1]:
            break
        else:
            p += 1
    # p is the number of the subinterval w falls into, i.e., p=i means
    # w falls into the ith subinterval $(x_i,x_{i+1}), and therefore
    # the value of the spline at w is
    # a_i+b_i*(w-x_i)+c_i*(w-x_i)^2+d_i*(w-x_i)^3.
    a = coeff[0]
    b = coeff[1]
    c = coeff[2]
    d = coeff[3]
    return a[p] + b[p] * (w - x[p]) + c[p] * (w - x[p]) ** 2 + d[p] * (w - x[p]) ** 3


# This function defines Newton polynomial interpolation
def newton(x, y, z):
    m = x.size  # here m is the number of data points, not the degree
    # of the polynomial
    a = diff(x, y)
    sum = a[0]
    pr = 1.0
    for j in range(m - 1):
        pr *= z - x[j]
        sum += a[j + 1] * pr
    return sum


def diff(x, y):
    m = x.size  # here m is the number of data points.
    # the degree of the polynomial is m-1
    a = np.zeros(m)
    for i in range(m):
        a[i] = y[i]
    for j in range(1, m):
        for i in np.flip(np.arange(j, m)):
            a[i] = (a[i] - a[i - 1]) / (x[i] - x[i - (j)])
    return a


# The functions below are for cubic B-splines
def open_uniform_vector(m, n):
    u = np.zeros((m, 1), dtype=float)
    j = 1
    for i in range(m):
        if i <= n:
            u[i] = 0.0
        elif i < m - (n + 1):
            u[i] = 1.0 / (m - 2 * (n + 1) + 1) * j
            j += 1
        else:
            u[i] = 1.0
    return u.flatten()


def basic_function(u, j, k, t):
    w1 = 0.0
    w2 = 0.0
    if k == 0:
        if u[j] < t <= u[j + 1]:
            var = 1.0
        else:
            var = 0.0
    else:
        if (u[j + k + 1] - u[j + 1]) != 0:
            w1 = (
                basic_function(u, j + 1, k - 1, t)
                * (u[j + k + 1] - t)
                / (u[j + k + 1] - u[j + 1])
            )
        if (u[j + k] - u[j]) != 0:
            w2 = basic_function(u, j, k - 1, t) * (t - u[j]) / (u[j + k] - u[j])
        var = w1 + w2
    return var


# %% [markdown] id="XCrdSUIV_S-v"
# ## Part 1: Interpolation in 1-D
#
# Here, we will look at a few common ways of achieving a continuous curve given a set of points. Note that depending on what the goal is, this curve need not necessarily interpolate the points.
#
# The first case is simple linear interpolation. As input data, we just use random noise.

# %% id="jkwyutlg_S-v"
# First, generate some data. Note that each time you run this
# you will get a different set of points. If you want to control this,
# set the random seed by uncommenting the line below.
np.random.seed(120)
mu = 1
sigma = 0.5
sample = 20
xleft = 0.0
xright = 20.0
y = np.random.normal(mu, sigma, size=sample)
x = np.linspace(xleft, xright, sample)

# %% id="pov9Dsgg_S-y"
# Simple linear interpolation of the data
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(x, y, lw=2, color="blue")
ax.scatter(x, y, color="black")
# %% [markdown] id="fssxxf3S_S-0"
# There are no surprises here. However, if a model was represented by a set of points with linear interpolation, the discontinuities in gradient at the node points may be undesirable.
#
# An alternative is to use a polynomial interpolation that is naturally smooth. One option would be to scale the number of nodes to the number of polynomial coefficients, and carry out an exact fit. This is what is done with Newton polynomial interpolation. The continuous function can be written
#
# $$
# N_n(x)=c_0+\sum_{i=1}^n c_i \left(\prod_{j=0}^{i-1} (x-x_j)\right)
# $$
#
# where $(x_i,y_i)$ are the points that we wish to interpolate. The coefficients $c_i$ can be determined quite easily by setting $y(x_i)=N_n(x_i)$. Thus:
#
# $$
# \begin{align}
# y_0&=c_0\\
# y_1&=c_0+c_1(x_1-x_0)\\
# y_2&=c_0+c_1(x_2-x_0)+c_2(x_2-x_0)(x_2-x_1)\\
# &etc.
# \end{align}
# $$
#
# Thus, from the first equation, you can determine $c_0$, from the second $c_1$, from the third $c_2$, and so on. Once all the coefficients are determined, any point on the curve can be determined with the equation fo $N_n(x)$. This produces an infinitely differential smooth curve, which is nice, but there are drawbacks..... See what happens below.

# %% id="TVCYU6D-_S-0"
n = 1000
xaxis = np.linspace(xleft, xright, n)
interp = newton(x, y, xaxis)
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(xaxis, interp, lw=2, color="blue")
ax.scatter(x, y, color="black")
# %%
#
# copy the data, adding two more at equal sapce to first last point at same distance to the next point (so have a "-1" and "-2" point and a "21" and "22" point)
# then run the fit again, and see what happens.
# then clip the data to 0 and 20
x_new = np.concatenate(([-3, -2, -1], x, [21, 22, 23]))
y_new = np.concatenate(([y[0], y[0], y[0]], y, [y[-1], y[-1], y[-1]]))
x_axis_new = np.linspace(-3, 23, n)
interp_new = newton(x_new, y_new, x_axis_new)

mask = (x_axis_new >= xleft) & (x_axis_new <= xright)
x_clipped = x_axis_new[mask]
interp_clipped = interp_new[mask]

fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(x_clipped, interp_clipped, lw=2, color="blue")
ax.scatter(x, y, color="black")
ax.set_xlim(xleft, xright)
# %% [markdown] id="lsJpZbNX_S-2"
# Describe what you see. Why do you think this happens? In the first code cell in this section, change the value of "sample" to 3, and see what happens. Gradually increase it until the interpolation starts to break down.
#
# ---
#
# As you can see, polynomial interpolation works quite well for a few points, which corresponds to a low order polynomial. However, it is pretty useless for even modest numbers of points.
#
# This observation has inspired an alternative approach for achieving a smooth interpolation, which involves suturing together piecewise polynomials of low order. This has the advantage that it is possible to avoid the exotic behaviour that you observed above. The downside is that continuity between the polynomial segments has to be sacrificed, but it is still possible to get a smooth interpolation that suppresses unrealistic behaviour.
#
# ---
#
# Natural cubic splines is a popular method that involves joining together cubic polynomials. In this approach, each polynomial (or spline) is joined together such that it is continuous in curvature (or the 2nd derivative) at the join point (i.e. at each node), and has zero curvature at the end points (i.e. becomes straight). It turns out, however, that to compute the coefficients, a tridiagonal system of equations needs to be solved. Furthermore, natural cubic splines have a global basis, which means that perturbing any of the nodes can have a global influence on the set of cubic polynomials. However, it is a distinct improvement over using a single nth order polynomial, as demonstrated below.

# %% id="ISNwugZP_S-4"
# This implements natural cubic spline interpolation for a set of points
# (x,y).
n = 1000
yaxis = [None] * n
coeff = CubicNatural(x, y)
i = -1
while i < n - 1:
    i += 1
    yaxis[i] = CubicNaturalEval(xaxis[i], x, coeff)
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(xaxis, yaxis, lw=2, color="blue")
ax.scatter(x, y, color="black")
# %% [markdown] id="8LzDCtuD_S-5"
# Clearly, this result is much more satisfactory compared to interpolation using a single polynomial. However, there is still clear evidence of overshoot, which may produce undesirable results.
#
# In the python package scipy, there is a powerful subpackage called interpolation that has many different options for interpolating data in one or more dimensions using regular or irregular grids. It is demonstrated below with make_lsq_spine, which does a best fit cubic spline to the set of points. In this case, the number of splines can be varied, and doesn't necessarily have to equal the number of nodes (minus one). If there are fewer splines, then they cannot in general interpolate the nodes, and an approximating spline is produced. In the code cell below, this is controlled by nk, which specifies the number of knot points, or joins between the polynomial segments. At the moment it is set to half the number of points. Try changing this to a few other values and see what happens.

# %% id="pLNLEKMw_S-6"
import scipy.interpolate as interpolate

k = 3
nk = int(sample / 1.1)
knots = np.linspace(x[0], x[-1], nk)
t = np.r_[(x[0],) * 3, knots, (x[-1],) * 3]
spline = interpolate.make_lsq_spline(x, y, t, k)
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(xaxis, spline(xaxis), lw=2, color="blue")
ax.scatter(x, y, color="black")


# %% [markdown] id="uCzErD3R_S-7"
# So far, natural cubic splines appear to do a pretty good job, but what happens when the data contains sharp jumps?
#
# As an exercise, generate a boxcar function using the evenly spaced points below, i.e. set ya=0 from i=0 to sample/3, ya=1 from i=sample/3 to 2*sample/3, and ya=0 from i=2*sample/3 to sample, and then plot the result.

# %% id="a7VCx053_S-9"
xleft = 0.0
xright = 20.0
sample = 20
xaxis = np.linspace(xleft, xright, sample)
ya = np.zeros(sample)
ya[int(sample / 3) : int(2 * sample / 3)] = 1
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(xaxis, ya, lw=2, color="blue")
ax.scatter(xaxis, ya, color="black")


# %% [markdown] id="-Raku4D1_S--"
# Linear interpolation obviously makes good sense here, but let's see what happens if natural cubic splines are used to interpolate these points.

# %% id="flEb7aPN_S--"
n = 1000

xaxis_dense = np.linspace(xleft, xright, n)  # Create a denser x-axis for evaluation
yaxis = [None] * n
coeff = CubicNatural(xaxis, ya)
i = -1
while i < n - 1:
    i += 1
    yaxis[i] = CubicNaturalEval(xaxis_dense[i], xaxis, coeff)  # Use xaxis_dense here
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(xaxis_dense, yaxis, lw=2, color="blue")  # Plot against xaxis_dense
ax.scatter(xaxis, ya, color="black")


# %% [markdown] id="b4Fud99J_S-_"
# What do you notice, and why do you think this happens?
#
# Clearly, this is not desirable behaviour. Let's see what happens if we try make_lsq_spline instead.

# %% id="d0qlOE1l_S_A"
k = 3
nk = int(sample / 3)
knots = np.linspace(xaxis[0], xaxis[-1], nk)
t = np.r_[(xaxis[0],) * 3, knots, (xaxis[-1],) * 3]
spline = interpolate.make_lsq_spline(xaxis, ya, t, k)
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(xaxis, spline(xaxis), lw=2, color="blue")
ax.scatter(xa, ya, color="black")
# %% [markdown] id="IQMuKk8H_S_B"
# This result is also not very desirable.
#
# The bottom line is that smooth interpolating polynomial functions are pretty poor at representing sharp transitions. This has implications for representing model structure; for example, if we represent the Earth's velocity field by a grid of points and use cubic-spine interpolation, but it turns out that there are sharp transitions in the velocity (e.g. across faults or at terrain boundaries), then the above effect could be introduced.
#
# ---
#
# An alternative approach is to use approximating splines, such as cubic B-splines, which we discussed in the lecture. These splines are not required to interpolate the points, which results in greater freedom in how they can best produce a continuous model from the points.
#
# In this scenario, it is better to view the nodes as control points, which control the shape of the model, rather than the nodes being discrete sample points of the model. This concept comes from computer graphics and animation, where complex shapes (people, cars etc) are represented by a mesh of control points, which can be moved around to adjust the smooth properties of the underlying model. If you use Illustrator or Inkscape, you likely would have encountered this concept before.
#
# Below, we will use cubic B-spline functions to represent the box car function above. As such, the set of points will be treated as control points which control the shape of the continuous curve.

# %% id="MbRh4yHS_S_C"
P = np.array([xa, ya])
p = P.shape[1]
nn = 1
m = p + nn + 1
u = open_uniform_vector(m, nn)
t = np.linspace(0.0, u[-1], int(u[-1] / 0.01))
S = np.zeros((2, len(t)))
S[:, 0] = P[:, 0]
for i in range(len(t)):
    if i == 0:
        continue
    for j in range(p):
        b = basic_function(u, j, nn, t[i])
        S[:, i] = S[:, i] + P[:, j] * b
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(S[0, :], S[1, :], lw=2, color="blue")
ax.scatter(xa, ya, color="black")
# %% [markdown] id="cwRjn8a9_S_D"
# As you can see, it produces a much more reasonable "model" with no undesirable oscillations. The variable nn in the above code controls the order of the polynomial; try playing around with this value to see what happens.

# %% [markdown] id="RYnCxUvV_S_E"
# ## Part 2: Interpolation in 2-D
#
# In this section, we investigate how to carry out interpolation in 2-D. To begin with, we generate some synthetic data.
#

# %% id="tRogY36u_S_E"
import random

xleft = 0.0
xright = 20.0
yleft = 0.0
yright = 20.0
sample = 5
x = np.linspace(xleft, xright, sample)
y = np.linspace(yleft, yright, sample)
X, Y = np.meshgrid(x, y)
mu = 1
sigma = 0.5
Z = [[random.random() for i in range(sample)] for j in range(sample)]

# %% [raw] id="TOoThZyS_S_E"
# We can plot this using contourf (below), but this offers only one kind of interpolation.

# %% id="vTVCarR7_S_E"
fig, ax = plt.subplots(figsize=(7, 7))
cf = ax.contourf(X, Y, Z, 10000, cmap="jet", sample=200)
fig.colorbar(cf, ax=ax)
ax.scatter(X, Y, color="black")
# %% [markdown] id="ubH0Igb4_S_G"
# This appears to be some kind of pseudo-linear interpolation. If the goal is to represent a layer interface, for example, this may not be ideal. In fact, if you increase sample=5 to sample=20, for example, the appearence is still non-physical. This is because contourf works best if it subsamples an already smooth surface.
#
# Below, we use griddata to subsample the input grid using cubic spline interpolation.

# %% id="xmC5CDk0_S_G"
from scipy.interpolate import griddata

xi, yi = np.mgrid[0:30, 0:30]
nsub = 20  # This is the number of sub-samples for interpolation
x1 = np.linspace(xleft, xright, nsub * sample)
y1 = np.linspace(yleft, yright, nsub * sample)
xi, yi = np.meshgrid(x1, y1)
zu = np.ravel(Z)
xu = np.ravel(X)
yu = np.ravel(Y)
# This is the interpolation part. Options include 'cubic', 'nearest' and 'linear'
zi = griddata((xu, yu), zu, (xi, yi), method="cubic")
fig, ax = plt.subplots(figsize=(7, 7))
cf = ax.contourf(xi, yi, zi, 100, cmap="viridis")
fig.colorbar(cf, ax=ax)
ax.scatter(X, Y, color="black")
# %% [markdown] id="Qrgxg3fE_S_G"
# Clearly, this gives a smoother model, which may be preferable.
#
# griddata can also be applied to irregular grids of points, as demonstrated below.

# %% id="56F8pYDt_S_H"
sample = 500
x1 = np.linspace(xleft, xright, sample)
y1 = np.linspace(yleft, yright, sample)
xi, yi = np.meshgrid(x1, y1)
npts = 20
px, py = np.random.choice(x1, npts), np.random.choice(y1, npts)
mu = 1
sigma = 0.5
np.random.seed(150)
pz = np.random.normal(mu, sigma, size=npts)
print("minumum and maximum vertex values are ", min(pz), "and", max(pz))
zi = griddata((px, py), pz, (xi, yi), method="cubic")
fig, ax = plt.subplots(figsize=(7, 7))
cf = ax.contourf(xi, yi, zi, 100, cmap="jet")
fig.colorbar(cf, ax=ax)
ax.scatter(px, py, color="black")
# %% [markdown] id="FJPZtZ7S_S_H"
# It works, but is arguably not ideal: there is likely to be overshoot (compare the min and max output values with the limits of the colour bar), and some features appear non-smooth and distorted. This is because polynomial fitting with unstructured grids is not a simple task.
#
# Another way to describe a continuum given an irregular set of nodes is to use Voronoi cells. This was briefly described in Lecture 3, and can be thought of as the shape made from circular wavefronts emanating from each point at the same velocity and starting at the same time. When a circle impinges on a neighbouring circle, the point at which they overlap becomes stationary. This draws out an unstructured mesh known as a Voronoi cell, as demonstrated below.
#
#
# Note: If you get an error message like "TypeError: \_held_figure() takes from 2 to 3 positional arguments but 4 were given", then you will need to upgrade scipy to a later version.
#

# %% id="31AFu1VY_S_H"
import matplotlib as mpl
import matplotlib.cm as cm
from scipy.spatial import Voronoi, voronoi_plot_2d

#
xy = np.vstack((px, py)).T
# add 4 distant dummy points
xy = np.append(xy, [[999, 999], [-999, 999], [999, -999], [-999, -999]], axis=0)
# Determine the Voronoi cells
vor = Voronoi(xy)
fig = plt.figure(figsize=(10, 8))
ax = plt.subplot2grid((16, 20), (0, 17), colspan=1, rowspan=16)
ax2 = plt.subplot2grid((16, 20), (0, 0), colspan=16, rowspan=16)
# creates a colourbar on the first subplot
minima = min(pz)
maxima = max(pz)
norm = mpl.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
mapper = cm.ScalarMappable(norm=norm, cmap=cm.jet)
cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cm.jet, norm=norm, orientation="vertical")
mpl.rcParams.update({"font.size": 15})
# Plot Voronoi cells
voronoi_plot_2d(
    vor,
    show_vertices=False,
    line_colors="black",
    line_width=2,
    line_alpha=0.6,
    point_size=8,
    ax=ax2,
)
# Fill in the polygons
for r in range(len(vor.point_region)):
    region = vor.regions[vor.point_region[r]]
    if not -1 in region:
        polygon = [vor.vertices[i] for i in region]
        plt.fill(*zip(*polygon), color=mapper.to_rgba(pz[r]))
# fix the range of axes
plt.xlim([xleft, xright]), plt.ylim([yleft, yright])
plt.show()

# %% [markdown] id="JhfewDzO_S_I"
# Of course, one could argue that this looks unphysical, but that hasn't stopped its widespread use in various Earth Sciences applications, including tomography. Interestingly, essentially the same result can be achieved in the previous code cell by changing "cubic" to "nearest".
#
# ---
#
# done using the Triangulation routine from matplotlib.

# %% id="LuqpfMQ3_S_I"
import matplotlib.tri as mtri

triang = mtri.Triangulation(px, py)
fig, ax = plt.subplots(figsize=(7, 7))
ax.tricontourf(triang, pz, 100, cmap="jet")
ax.scatter(px, py, color="black")


# %% [markdown] id="G8n6ouA5_S_J"
# ## Part 3: 3-D Examples
#
# To run this example, you will need to install pyvista with conda. To do so, use something like:
#
# ```
# conda config --add channels conda-forge
# conda create -n pyvista python=3.7
# conda activate pyvista
# conda install vtk
# conda install pyqt
# conda install pyvista
# ```
#
# Note: You may also have to run "conda install -c conda-forge jupyter" in the obspy environment if you get an error like "ModuleNotFoundError: No module named 'pyvista'" when you run the cell below.
#
# Alternatively, you could just install in your base environment. This avoids having to install jupyter (and potentiall scipy and matplotlib) in this new environment. If running in colab, this is what is being done below.
#
# ---
#
# pyvista is a very powerful package that interfaces with the visualisation toolkit, and allows meshing and visualisation of large complex datasets in 3-D. Below, we will take a look at a few examples that demonstrate how it can be used.
#
# The first example demonstrates how a terrane conforming mesh can be generated given some topographic data (or DEM model). This might be useful in the numerical modelling of surface processes, for example.
# %% id="oEtXPZ9-ACpi"
# run this cell if you are using colab - pyvista is particular about plotting on online notebooks
# colab updates could break this - check the documentation https://tutorial.pyvista.org/getting-started.html if no plots appear
# !apt-get install -qq xvfb libgl1-mesa-glx
# !pip install pyvista -qq
import pyvista as pv

pv.set_jupyter_backend("static")
pv.global_theme.notebook = True
pv.start_xvfb()

# %% id="N9Ro59aN_S_J"
# First, a DEM example is imported, and a subset is plotted.
import pyvista as pv
from pyvista import examples

dem = examples.download_crater_topo()
subset = dem.extract_subset((500, 900, 400, 800, 0, 0), (5, 5, 1))
subset.plot(cpos="xy")

# %% id="bTjB44qN_S_K"
# This plots the DEM as a 3-D surface projection
terrain = subset.warp_by_scalar()
terrain.plot()

# %% [markdown] id="5_5Jjwgg_S_K"
# The next step involves creating a 3-D mesh that conforms with the surface topography. pv.StructureGrid generates hexahedrons from topologically regular input data.

# %% id="T6avrszi_S_K"
z_cells = np.array([25] * 5 + [35] * 3 + [50] * 2 + [75, 100])

xx = np.repeat(terrain.x, len(z_cells), axis=-1)
yy = np.repeat(terrain.y, len(z_cells), axis=-1)
zz = np.repeat(terrain.z, len(z_cells), axis=-1) - np.cumsum(z_cells).reshape(
    (1, 1, -1)
)

mesh = pv.StructuredGrid(xx, yy, zz)
mesh["Elevation"] = zz.ravel(order="F")
cpos = [
    (1826736.796308761, 5655837.275274233, 4676.8405505181745),
    (1821066.1790519988, 5649248.765538796, 943.0995128226014),
    (-0.2797856225380979, -0.27966946337594883, 0.9184252809434081),
]

mesh.plot(show_edges=True, lighting=False, cpos=cpos)

# %% [markdown] id="ilaayHcC_S_K"
# pyvista also has sophisticated 3-D unstructured meshing capability for irregular node distributions, as demonstrated below.

# %% id="Lbq9D0Qn_S_L"
grid = examples.download_letter_a()

cpos = [
    (2.704583323659036, 0.7822568412034183, 1.7251126717482546),
    (3.543391913452799, 0.31117673768140197, 0.16407006760146028),
    (0.1481171795711516, 0.96599698246102, -0.2119224645762945),
]


centers = grid.cell_centers()

p = pv.Plotter()
p.add_mesh(grid, show_edges=True, opacity=0.5, line_width=1)
p.add_mesh(centers, color="b", point_size=4.0, render_points_as_spheres=True)
p.show(cpos=cpos)

# %% [markdown] id="XCrSKEYE_S_M"
# pyvista is popular in Earth Sciences applications for visualising 3-D models. In the example below, a 3-D density model is plotted of the Laguna del Maule volcanic field, Chile, which was created through inversion of surface gravity measurements. See  https://www.sciencedirect.com/science/article/pii/S0012821X16306410 for more details.
#
# First we import some modules, which you may need to install with conda if they are not already present.

# %% id="WtN-VhQQ_S_M"
import os
import tarfile

import discretize

# %% [markdown] id="XjR-IaUq_S_M"
# Here, we import the data.

# %% id="Y2GNS-uG_S_N"
# Download Topography and Observed gravity data
url = "https://storage.googleapis.com/simpeg/Chile_GRAV_4_Miller/Chile_GRAV_4_Miller.tar.gz"
downloads = discretize.utils.download(url, overwrite=True)
basePath = downloads.split(".")[0]

# unzip the tarfile
tar = tarfile.open(downloads, "r")
tar.extractall()
tar.close()

# Download the inverted model
f = discretize.utils.download(
    "https://storage.googleapis.com/simpeg/laguna_del_maule_slicer.tar.gz",
    overwrite=True,
)
tar = tarfile.open(f, "r")
tar.extractall()
tar.close()

# %% [markdown] id="7r7D7wq8_S_N"
# Here, the data objects are assembled.

# %% id="syEEdLqg_S_N"
# Load the mesh/data
mesh = discretize.load_mesh(os.path.join("laguna_del_maule_slicer", "mesh.json"))
models = {"Lpout": np.load(os.path.join("laguna_del_maule_slicer", "Lpout.npy"))}

# Get the PyVista dataset of the inverted model
dataset = mesh.to_vtk(models)
dataset.set_active_scalars("Lpout")

# Load topography points from text file as XYZ numpy array
topo_pts = np.loadtxt("Chile_GRAV_4_Miller/LdM_topo.topo", skiprows=1)
# Create the topography points and apply an elevation filter
topo = pv.PolyData(topo_pts).delaunay_2d().elevation()

# Load the gravity data from text file as XYZ+attributes numpy array
grav_data = np.loadtxt("Chile_GRAV_4_Miller/LdM_grav_obs.grv", skiprows=1)
print("gravity file shape: ", grav_data.shape)
# Use the points to create PolyData
grav = pv.PolyData(grav_data[:, 0:3])
# Add the data arrays
grav.point_data["comp-1"] = grav_data[:, 3]
grav.point_data["comp-2"] = grav_data[:, 4]
grav.set_active_scalars("comp-1")

# %% [markdown] id="WJIWPr7F_S_O"
# Finally, the model is rendered in 3-D.

# %% id="HtAblPhw_S_O"
# Create display parameters for inverted model
dparams = dict(
    show_edges=False,
    cmap="bwr",
    clim=[-0.6, 0.6],
)

# Apply a threshold filter to remove topography
#  no arguments will remove the NaN values
dataset_t = dataset.threshold()

# Extract volumetric threshold
threshed = dataset_t.threshold(-0.2, invert=True)

# Create the rendering scene
p = pv.Plotter()
# add a grid axes
p.show_grid()

# Add spatially referenced data to the scene
p.add_mesh(dataset_t.slice("x"), **dparams)
p.add_mesh(dataset_t.slice("y"), **dparams)
p.add_mesh(threshed, **dparams)
p.add_mesh(
    topo,
    opacity=0.45,
    color="white",
    # cmap='gist_earth', clim=[1.7e+03, 3.104e+03],
)
p.add_mesh(grav, cmap="viridis", point_size=15, render_points_as_spheres=True)

# Here is a nice camera position we manually found:
cpos = [
    (395020.7332989303, 6039949.0452080015, 20387.583125699253),
    (364528.3152860675, 6008839.363092581, -3776.318305935185),
    (-0.3423732500124074, -0.34364514928896667, 0.8744647328772646),
]
p.camera_position = cpos


# Render the scene!
p.show(window_size=[1024, 768])

# %% [markdown] id="Y0TrDv0p_S_O"
# The top colour scale indicates the gravity residual in mGal, and the bottom colour scale indicates the density anomaly in grams per cubic centimeter. The 3-D density model is parameterized in terms of constant density blocks, with a total of 190,440 blocks distributed uniformly in latitude and longitude, but with thickness increasing as a function of depth. The negative gravity anomaly is interpreted as a magma reservoir beneath the volcanic edifice. Of course, with the relatively small number of gravity measurements available, there is no way that 190,440 density blocks could be independently constrained. Hence, regularisation must be introduced to solve the inverse problem - see https://www.sciencedirect.com/science/article/pii/S0012821X16306410 for more details.
