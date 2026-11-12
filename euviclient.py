from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient


class EUVIClient(GenericClient):
    """
    STEREO SECCHI EUVI client for NASA SSC L0_YMD archive.
    """

    baseurl = (
        "https://stereo-ssc.nascom.nasa.gov/data/ins_data/secchi/"
        "L0_YMD/{spacecraft}/img/euvi/%Y/%m/%d/"
        "%Y%m%d_%H%M%S_{wave:3d}eu{spacecraft:1s}.fts"
    )

    pattern = (
        "{year:4d}/{month:2d}/{day:2d}/"
        "{year:4d}{month:2d}{day:2d}_{hour:2d}{minute:2d}{second:2d}_"
        "{wave:3d}eu{spacecraft:1s}.fts"
    )

    required = {a.Time, a.Instrument}

    @classmethod
    def _can_handle_query(cls, *query):
        return cls.check_attr_types_in_query(
            query,
            required_attrs=cls.required,
            optional_attrs={a.Source, a.Wavelength},
        )

    @classmethod
    def _get_match_dict(cls, *args, **kwargs):
        matchdict = super()._get_match_dict(*args, **kwargs)

        # Default to STEREO-A because your example ends in euA.fts
        matchdict.setdefault("spacecraft", "a")

        # Translate Source/STEREO_A or Source/STEREO_B into archive directory.
        for arg in args:
            if isinstance(arg, a.Source):
                value = arg.value.lower()
                if "stereo_a" in value or value in {"ahead", "sta", "a"}:
                    matchdict["spacecraft"] = "a"
                elif "stereo_b" in value or value in {"behind", "stb", "b"}:
                    matchdict["spacecraft"] = "b"

            if isinstance(arg, a.Wavelength):
                # EUVI archive filenames use e.g. 171, 195, 284, 304.
                matchdict["wave"] = int(arg.min.to_value("Angstrom"))

        return matchdict

    @property
    def info_url(self):
        return "https://stereo-ssc.nascom.nasa.gov/data/ins_data/secchi/L0_YMD/"


# Register with Fido
from sunpy.net import Fido

Fido.register(EUVIClient)