import os
import pytest
import pandas as pd

import pyorc
EXAMPLE_DATA_DIR = os.path.join(os.path.split(__file__)[0], "..", "examples", "ngwerere")

# sample data, for Ngwerere
@pytest.fixture
def gcps():
    return dict(
        src=[
            [1421, 1001],
            [1251, 460],
            [421, 432],
            [470, 607]
        ],
        dst=[
            [642735.8076, 8304292.1190],  # lowest right coordinate
            [642737.5823, 8304295.593],  # highest right coordinate
            [642732.7864, 8304298.4250],  # highest left coordinate
            [642732.6705, 8304296.8580]  # highest right coordinate
        ],
        z_0=1182.2,
        h_ref=0.
    )


@pytest.fixture
def lens_position():
    return [642732.6705, 8304289.010, 1188.5]

@pytest.fixture
def corners():
    return [
        [292, 817],
        [50, 166],
        [1200, 236],
        [1600, 834]
    ]


@pytest.fixture
def lens_pars():
    return {
        "k1": 0,
        "c": 2.0,
        "f": 1.0
    }


@pytest.fixture
def cam_config(gcps, lens_position, lens_pars, corners):
    return pyorc.CameraConfig(
        gcps=gcps,
        lens_position=lens_position,
        lens_pars=lens_pars,
        corners=corners,
        window_size=25,
        resolution=0.01,
        crs=32735
        )


@pytest.fixture
def cross_section():
    fn = os.path.join(EXAMPLE_DATA_DIR, "ngwerere_cross_section.csv")
    return pd.read_csv(fn)


@pytest.fixture
def cam_config_fn():
    return os.path.join(EXAMPLE_DATA_DIR, "ngwerere.json")

@pytest.fixture
def h_a():
    return 0.


@pytest.fixture
def cam_config_dict():
    return {
        'crs': 'PROJCRS["WGS 84 / UTM zone 35S",BASEGEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],MEMBER["World Geodetic System 1984 (G2139)"],ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4326]],CONVERSION["UTM zone 35S",METHOD["Transverse Mercator",ID["EPSG",9807]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",27,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["Scale factor at natural origin",0.9996,SCALEUNIT["unity",1],ID["EPSG",8805]],PARAMETER["False easting",500000,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",10000000,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["metre",1]],USAGE[SCOPE["Engineering survey, topographic mapping."],AREA["Between 24°E and 30°E, southern hemisphere between 80°S and equator, onshore and offshore. Botswana. Burundi. Democratic Republic of the Congo (Zaire). Rwanda. South Africa. Tanzania. Uganda. Zambia. Zimbabwe."],BBOX[-80,24,0,30]],ID["EPSG",32735]]',
        'resolution': 0.01,
        'lens_position': [642732.6705, 8304289.01, 1188.5],
        'gcps': {
            'src': [[1421, 1001], [1251, 460], [421, 432], [470, 607]],
            'dst': [
                [642735.8076, 8304292.119],
                [642737.5823, 8304295.593],
                [642732.7864, 8304298.425],
                [642732.6705, 8304296.858]
            ],
            'h_ref': 0.0,
            'z_0': 1182.2
        },
        'window_size': 25,
        'corners': [[292, 817], [50, 166], [1200, 236], [1600, 834]],
        'lens_pars': {
            'k1': 0,
            'c': 2.0,
            'f': 1.0
        }
    }


@pytest.fixture
def cam_config_str():
    return '{\n    "crs": "PROJCRS[\\"WGS 84 / UTM zone 35S\\",BASEGEOGCRS[\\"WGS 84\\",ENSEMBLE[\\"World Geodetic System 1984 ensemble\\",MEMBER[\\"World Geodetic System 1984 (Transit)\\"],MEMBER[\\"World Geodetic System 1984 (G730)\\"],MEMBER[\\"World Geodetic System 1984 (G873)\\"],MEMBER[\\"World Geodetic System 1984 (G1150)\\"],MEMBER[\\"World Geodetic System 1984 (G1674)\\"],MEMBER[\\"World Geodetic System 1984 (G1762)\\"],MEMBER[\\"World Geodetic System 1984 (G2139)\\"],ELLIPSOID[\\"WGS 84\\",6378137,298.257223563,LENGTHUNIT[\\"metre\\",1]],ENSEMBLEACCURACY[2.0]],PRIMEM[\\"Greenwich\\",0,ANGLEUNIT[\\"degree\\",0.0174532925199433]],ID[\\"EPSG\\",4326]],CONVERSION[\\"UTM zone 35S\\",METHOD[\\"Transverse Mercator\\",ID[\\"EPSG\\",9807]],PARAMETER[\\"Latitude of natural origin\\",0,ANGLEUNIT[\\"degree\\",0.0174532925199433],ID[\\"EPSG\\",8801]],PARAMETER[\\"Longitude of natural origin\\",27,ANGLEUNIT[\\"degree\\",0.0174532925199433],ID[\\"EPSG\\",8802]],PARAMETER[\\"Scale factor at natural origin\\",0.9996,SCALEUNIT[\\"unity\\",1],ID[\\"EPSG\\",8805]],PARAMETER[\\"False easting\\",500000,LENGTHUNIT[\\"metre\\",1],ID[\\"EPSG\\",8806]],PARAMETER[\\"False northing\\",10000000,LENGTHUNIT[\\"metre\\",1],ID[\\"EPSG\\",8807]]],CS[Cartesian,2],AXIS[\\"(E)\\",east,ORDER[1],LENGTHUNIT[\\"metre\\",1]],AXIS[\\"(N)\\",north,ORDER[2],LENGTHUNIT[\\"metre\\",1]],USAGE[SCOPE[\\"Engineering survey, topographic mapping.\\"],AREA[\\"Between 24\\u00b0E and 30\\u00b0E, southern hemisphere between 80\\u00b0S and equator, onshore and offshore. Botswana. Burundi. Democratic Republic of the Congo (Zaire). Rwanda. South Africa. Tanzania. Uganda. Zambia. Zimbabwe.\\"],BBOX[-80,24,0,30]],ID[\\"EPSG\\",32735]]",\n    "resolution": 0.01,\n    "lens_position": [\n        642732.6705,\n        8304289.01,\n        1188.5\n    ],\n    "gcps": {\n        "src": [\n            [\n                1421,\n                1001\n            ],\n            [\n                1251,\n                460\n            ],\n            [\n                421,\n                432\n            ],\n            [\n                470,\n                607\n            ]\n        ],\n        "dst": [\n            [\n                642735.8076,\n                8304292.119\n            ],\n            [\n                642737.5823,\n                8304295.593\n            ],\n            [\n                642732.7864,\n                8304298.425\n            ],\n            [\n                642732.6705,\n                8304296.858\n            ]\n        ],\n        "h_ref": 0.0,\n        "z_0": 1182.2\n    },\n    "lens_pars": {\n        "k1": 0,\n        "c": 2.0,\n        "f": 1.0\n    },\n    "window_size": 25,\n    "corners": [\n        [\n            292,\n            817\n        ],\n        [\n            50,\n            166\n        ],\n        [\n            1200,\n            236\n        ],\n        [\n            1600,\n            834\n        ]\n    ]\n}'


@pytest.fixture
def vid():
    vid = pyorc.Video(
        os.path.join(EXAMPLE_DATA_DIR, "ngwerere_20191103.mp4"),
        start_frame=0,
        end_frame=2,
    )
    yield vid
    # vid.release()
    # del vid
    # return

@pytest.fixture
def vid_cam_config(cam_config):
    vid = pyorc.Video(
        os.path.join(EXAMPLE_DATA_DIR, "ngwerere_20191103.mp4"),
        start_frame=0,
        end_frame=2,
        camera_config=cam_config,
        h_a=0.
    )
    yield vid


@pytest.fixture
def vid_cam_config_stabilize(cam_config):
    vid = pyorc.Video(
        os.path.join(EXAMPLE_DATA_DIR, "ngwerere_20191103.mp4"),
        start_frame=0,
        end_frame=125,
        camera_config=cam_config,
        h_a=0.,
        stabilize="fixed"
    )
    yield vid


@pytest.fixture
def frames_grayscale(vid_cam_config):
    return vid_cam_config.get_frames()


@pytest.fixture
def frames_rgb_stabilize(vid_cam_config_stabilize):
    return vid_cam_config_stabilize.get_frames(method="rgb")


@pytest.fixture
def frames_rgb(vid_cam_config):
    return vid_cam_config.get_frames(method="rgb")




@pytest.fixture
def frames_proj(frames_grayscale):
    return frames_grayscale.frames.project()


@pytest.fixture
def ani_mp4():
    yield "temp.mp4"
    os.remove("temp.mp4")


@pytest.fixture
def piv(frames_proj):
    # provide a short piv object
    return frames_proj.frames.get_piv()


@pytest.fixture
def piv_transect(piv, cross_section):
    x, y, z = cross_section["x"], cross_section["y"], cross_section["z"]
    # provide a short piv object
    return piv.velocimetry.get_transect(x, y, z)


