import numpy as np
import xarray as xr
from pyorc import helpers
import pyorc.plot as plot_orc

from .orcbase import ORCBase


@xr.register_dataset_accessor("transect")
class Transect(ORCBase):
    def __init__(self, xarray_obj):
        super(Transect, self).__init__(xarray_obj)

    def vector_to_scalar(self, angle_method=0, v_x="v_x", v_y="v_y"):
        """
        Set "v_eff" and "v_dir" variables as effective velocities over cross-section, and its angle

        :param v_x: str, variable containing (t, points) time series in cross section with x-directional velocities.
        :param v_y: str, variable containing (t, points) time series in cross section with y-directional velocities.
        :param angle_method: if set to 0, then angle of cross section is determined with left to right bank coordinates,
            otherwise, it is determined per section.
        :return: DataArray(t, points), time series in points with velocities perpendicular to cross section.

        """
        xs = self._obj["x"].values
        ys = self._obj["y"].values
        # find points that are located on the area of interest
        idx = np.isfinite(xs)
        xs = xs[idx]
        ys = ys[idx]
        if angle_method == 0:
            x_left, y_left = xs[0], ys[0]
            x_right, y_right = xs[-1], ys[-1]
            angle_da = np.arctan2(x_right - x_left, y_right - y_left)
        else:
            # start with empty angle
            angle = np.zeros(ys.shape)
            angle_da = np.zeros(self._obj["x"].shape)
            angle_da[:] = np.nan

            for n, (x, y) in enumerate(zip(xs, ys)):
                # determine the angle of the current point with its neighbours
                # check if we are at left bank
                # first estimate left bank angle
                undefined = True  # angle is still undefined
                m = 0
                while undefined:
                    # go one step to the left
                    m -= 1
                    if n + m < 0:
                        # we are at the left bank, so angle with left neighbour is non-existing.
                        x_left, y_left = xs[n], ys[n]
                        # angle_left = np.nan
                        undefined = False
                    else:
                        x_left, y_left = xs[n + m], ys[n + m]
                        if not ((x_left == x) and (y_left == y)):
                            # profile points are in another pixel, so estimate angle
                            undefined = False
                            angle_left = np.arctan2(x - x_left, y - y_left)

                # estimate right bank angle
                undefined = True  # angle is still undefined
                m = 0
                while undefined:
                    # go one step to the left
                    m += 1
                    if n + m >= len(xs) - 1:
                        angle_right = np.nan
                        undefined = False
                    else:
                        x_right, y_right = xs[n + m], ys[n + m]
                        if not ((x_right == x) and (y_right == y)):
                            # profile points are in another pixel, so estimate angle
                            undefined = False
                            angle_right = np.arctan2(x_right - x, y_right - y)
                angle[n] = np.nanmean([angle_left, angle_right])
            # add angles to array meant for data array
            angle_da[idx] = angle

        # compute angle of flow direction (i.e. the perpendicular of the cross section) and add as DataArray to ds_points
        flow_dir = angle_da - 0.5 * np.pi

        # compute per velocity vector in the dataset, what its angle is
        v_angle = np.arctan2(self._obj[v_x], self._obj[v_y])
        # compute the scalar value of velocity
        v_scalar = (self._obj[v_x] ** 2 + self._obj[v_y] ** 2) ** 0.5

        # compute difference in angle between velocity and perpendicular of cross section
        angle_diff = v_angle - flow_dir
        # compute effective velocity in the flow direction (i.e. perpendicular to cross section
        v_eff = np.cos(angle_diff) * v_scalar
        v_eff.attrs = {
            "standard_name": "velocity",
            "long_name": "velocity in perpendicular direction of cross section, measured by angle in radians, measured from up-direction",
            "units": "m s-1",
        }
        # set name
        v_eff.name = "v_eff_nofill"  # there still may be gaps in this series
        self._obj["v_eff_nofill"] = v_eff
        # store the angle for plotting purposes
        self._obj["v_dir"] = (("points"), np.ones(len(self._obj.points)) * flow_dir)
        self._obj["v_dir"].attrs = {
            "standard_name": "river_flow_angle",
            "long_name": "Angle of river flow in radians from North",
            "units": "rad"
        }

    def get_xyz_perspective(self):
        """
        Get camera-perspective column, row coordinates from cross-section points.

        :return:
        """
        z = (self._obj.zcoords - self.camera_config.gcps["z_0"] + self.camera_config.gcps["h_ref"]).values
        Ms = [self.camera_config.get_M_reverse(depth) for depth in z]
        # compute row and column position of vectors in original reprojected background image col/row coordinates
        cols, rows = zip(*[helpers.xy_to_perspective(x, y, self.camera_config.resolution, M, reverse_y=self.camera_config.shape[0]) for x, y, M in zip(self._obj.x.values, self._obj.y.values, Ms)])

        # ensure y coordinates start at the top in the right orientation
        shape_y, shape_x = self.camera_shape
        rows = shape_y - np.array(rows)
        cols = np.array(cols)
        return cols, rows


    def get_river_flow(self):
        """
        Integrate time series of depth averaged velocities [m2 s-1] into cross-section integrated flow [m3 s-1]
        estimating one or several quantiles over the time dimension. Depth average velocities must first have been
        estimated using get_q.
    
        :return: ds: xarray dataset, including variable "Q" which is cross-sectional integrated river flow [m3 s-1] for one or several quantiles.
            The time dimension no longer exists because of the quantile mapping, the point dimension no longer exists because of the integration over width
        """

        if "q" not in self._obj:
            raise ValueError('Dataset must contain variable "q", which is the depth-integrated velocity [m2 s-1], perpendicular to cross-section. Create this with ds.transect.get_q')
        # integrate over the distance coordinates (s-coord)
        Q = self._obj["q"].fillna(0.0).integrate(coord="scoords")
        Q.attrs = {
            "standard_name": "river_discharge",
            "long_name": "River Flow",
            "units": "m3 s-1",
        }
        # set name
        Q.name = "Q"
        self._obj["river_flow"] = Q


    def get_q(self, v_corr=0.9, quantiles=[0.05, 0.25, 0.5, 0.75, 0.95]):
        """
        Depth integrated velocity for quantiles of time series using a correction v_corr between surface velocity and
        depth-average velocity.

        :param v_corr: float, optional, correction factor (default: 0.9)
        :param quantiles: list of floats, optional, quantiles (0-1) over time to estimate depth-integrated velocity for
        :return: xr.Dataset, Transect for selected quantiles in time, including "q".
        """
        # aggregate to a limited set of quantiles
        ds = self._obj.quantile(quantiles, dim="time", keep_attrs=True)
        x = ds["xcoords"].values
        y = ds["ycoords"].values
        z = ds["zcoords"].values
        z_0 = self.camera_config.gcps["z_0"]
        h_ref =  self.camera_config.gcps["h_ref"]
        h_a = ds.h_a
        # add filled surface velocities with a logarithmic profile curve fit
        ds["v_eff"] = helpers.velocity_fill(x, y, z, ds["v_eff_nofill"], z_0, h_ref, h_a, groupby="quantile")
        # compute q for both non-filled and filled velocities
        ds["q_nofill"] = helpers.depth_integrate(z, ds["v_eff_nofill"], z_0, h_ref, h_a, v_corr=v_corr, name="q_nofill")
        ds["q"] = helpers.depth_integrate(z, ds["v_eff"], z_0, h_ref, h_a, v_corr=v_corr, name="q")
        return ds


    def plot(
        self,
        ax=None,
        mode="local",
        v_eff="v_eff",
        v_dir="v_dir",
        cbar_fontsize=15,
        kwargs = {},
    ):
        """
        plot velocimetry results across a transect as quiver plot. Plotting can be done in three modes:

        - "local": a simple planar view plot, with a local coordinate system in meters, with the top-left coordinate
          being the 0, 0 point, and ascending coordinates towards the right and bottom.
        - "geographical": a geographical plot, requiring the package `cartopy`, the results are plotted on a
            geographical axes, so that combinations with tile layers such as OpenStreetMap, or shapefiles can be made.
        - "camera": i.e. seen from the camera perspective. This is the most intuitive view for end users.
        :param ax: pre-defined axes object. If not set, a new axes will be prepared. In case `mode=="geographical"`, a
            cartopy GeoAxes needs to be provided, or will be made in case ax is not set. If an axes with background
            frame is provided (made through frames.plot) then the background must be plotted in the same mode as
            selected here.
        :param kwargs: dict, plotting parameters to be passed to matplotlib.pyplot.quiver, for plotting quiver arrows.
        :param v_x: str, name of variable in ds, containing x-directional (u) velocity component (default: "v_x")
        :param v_y: str, name of variable in ds, containing y-directional (v) velocity component (default: "v_y")
        :param cbar_fontsize: fontsize to use for the colorbar title (fontsize of tick labels will be made slightly
            smaller).
        :return: ax, axes object resulting from this function.
        """
        u = self._obj[v_eff] * np.sin(self._obj[v_dir])
        v = self._obj[v_eff] * np.cos(self._obj[v_dir])
        s = self._obj[v_eff]
        if mode == "local":
            x = "x"
            y = "y"
            theta = 0.
        elif mode == "geographical":
            import cartopy.crs as ccrs
            # add transform for GeoAxes
            kwargs["transform"] = ccrs.PlateCarree()
            x = "lon"
            y = "lat"
            aff = self.camera_config.transform
            theta = np.arctan2(aff.d, aff.a)
        ax = plot_orc.prepare_axes(ax=ax, mode=mode)
        f = ax.figure  # handle to figure

        p = plot_orc.quiver(ax, self._obj[x].values, self._obj[y].values, *[v.values for v in helpers.rotate_u_v(u, v, theta)], s,
                        **kwargs)
        if mode == "geographical":
            ax.set_extent(
                [self._obj[x].min() - 0.0002, self._obj[x].max() + 0.0002, self._obj[y].min() - 0.0002, self._obj[y].max() + 0.0002],
                crs=ccrs.PlateCarree())
        else:
            ax.axis('equal')
        cb = plot_orc.cbar(ax, p, size=cbar_fontsize)
        return ax
