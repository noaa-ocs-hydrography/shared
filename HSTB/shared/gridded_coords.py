import numpy as np

class Grid(object):
    ''' Class to compute array indices from position and vice versa.
    In HSTB module, currently used with an ESRI grids (ArcExt) and VR BAGs (SurveyOutline)

    The attributes x_edges and y_edges contain the coordinates for each cell.

    The attributes grid_val and grid_count are numpy arrays of the appropriate size IFF allocate is True in the constructor.
    Be aware that changing the cell_size or min/max x/y locations will reallocate the grid_val and grid_count arrays (deleteing all existing data)
    '''

    def __init__(self, lower_left_xy, nxy, cell_size, buffer_dist=0, allocate=True):
        """ Creates an object describing a rectangular grid.

        Parameters
        ----------
        lower_left_xy
            Tuple for lower left corner (x, y) position
        nxy
            Tuple of number of x cells and y cells
        cell_size
             Is either a single number for a square grid or a 2-tuple for x_size, ysize
        buffer_dist
            Amount to expand gridded area in all directions,   +/- X and Y
        allocate
            Whether to create a numpy array to hold data in.  Setting allocate=False implies you will just use the coordinate math.
        """
        self.x_edges = self.y_edges = None  # this will be replaced once the min/max x/y are set
        self.grid_val = self.grid_count = None  # this will be replaced IF allocate is True
        self.allocate = allocate
        try:
            self.cell_size_x, self.cell_size_y = cell_size
        except TypeError:
            self.cell_size_x = cell_size
            self.cell_size_y = cell_size
        # Identify spatial characteristics of input grid raster
        self.minx = lower_left_xy[0] - buffer_dist  # Desired grid cell size = 500 m ## BUFFER
        self.maxx = self.minx + nxy[0] * self.cell_size_x + buffer_dist
        self.miny = lower_left_xy[1] - buffer_dist  # Desired grid cell size = 500 m ## BUFFER
        self.maxy = self.miny + nxy[1] * self.cell_size_y + buffer_dist

    @property
    def cell_size_x(self):
        """ Cell size in X direction.
        Computed from Min/Max(X/Y)."""
        return self._cell_size_y

    @cell_size_x.setter
    def cell_size_x(self, value):
        self._cell_size_y = value
        self.reset_bounds()

    @property
    def cell_size_y(self):
        """Cell zise in Y direction.
        Computed from Min/Max(X/Y)."""
        return self._cell_size_y

    @cell_size_y.setter
    def cell_size_y(self, value):
        self._cell_size_y = value
        self.reset_bounds()

    @property
    def minx(self):
        """Minimum position of grid in X.
        Min/Max(X/Y) used to determine cell sizes."""
        return self._minx

    @minx.setter
    def minx(self, value):
        self._minx = value
        self.reset_bounds()

    @property
    def miny(self):
        """Minimum position of grid in Y.
        Min/Max(X/Y) used to determine cell sizes."""
        return self._miny

    @miny.setter
    def miny(self, value):
        self._miny = value
        self.reset_bounds()

    @property
    def maxx(self):
        """Maximum position of grid in X.
        Min/Max(X/Y) used to determine cell sizes."""
        return self._maxx

    @maxx.setter
    def maxx(self, value):
        self._maxx = value
        self.reset_bounds()

    @property
    def maxy(self):
        """Maximum position of grid in Y"""
        return self._maxy

    @maxy.setter
    def maxy(self, value):
        self._maxy = value
        self.reset_bounds()

    @property
    def orig_x(self):
        return self.minx

    @property
    def orig_y(self):
        return self.miny

    @property
    def origin(self) -> tuple:
        """Origin of grid (minx, miny) as a tuple"""
        return self.orig_x, self.orig_y

    def reset_bounds(self):
        try:
            self.x_edges = np.arange(self.orig_x, self.maxx + self.cell_size_x, self.cell_size_x)
            self.y_edges = np.arange(self.orig_y, self.maxy + self.cell_size_y, self.cell_size_y)
            if self.allocate:
                self.grid_val = self.zeros()
                self.grid_val.fill(np.nan)
                self.grid_count = self.zeros()
        except AttributeError:
            pass  # may not be set up yet

    # Define extents of Groundings Histogram based on extents of grid raster
    # Note: If Must keep origin at same grid cell node, set orig_x and orig_y as min coords of grid (bottom left)

    @property
    def orig(self) -> np.array:
        """Origin of grid as a numpy array (minx, miny)"""
        return np.array([self.orig_x, self.orig_y])  # Min x and y coordinate of grid raster; used to generate raster of Groundings

    @property
    def numx(self):
        """The number of cells in the X direction"""
        return len(self.x_edges)-1

    @property
    def numy(self):
        """The number of cells in the Y direction"""
        return len(self.y_edges)-1

    @property
    def numcol(self):
        """The number of columns of data (cells in X direction)"""
        return self.numx

    @property
    def numrow(self):
        """The number of rows of data (cells in Y direction)"""
        return self.numy

    def row_col_from_xy(self, x, y):
        """Returns the (Row,Col) based on the x,y position supplied.
        Really you probably want to use array_indices_from_xy as (row,col) equates to (Y, X)"""
        return self.row_index(y), self.col_index(x)

    def row_index(self, y):
        """Get the Row based on the Y position"""
        return (y - self.orig_y) / self.cell_size_y

    def col_index(self, x):
        """Get the Col based on the X position"""
        return (x - self.orig_x) / self.cell_size_x

    def array_indices_from_xy(self, inputarray):
        """Pass in a numpy array of XY values and returns the row,column indices as a numpy array"""
        output = np.array((inputarray - np.array(self.origin)) / np.array((self.cell_size_x, self.cell_size_y)),
                          dtype=np.int32)  # Translating polygon enveloppe indices to grid indices
        return output

    def zeros(self, dtype=np.float64):
        """Get a zero numpy array with the size matching this object's rows and columns (x cells and y cells counts)"""
        return np.zeros([self.numx, self.numy], dtype=dtype)
