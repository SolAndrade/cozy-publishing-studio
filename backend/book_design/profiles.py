from dataclasses import dataclass,replace
from enum import StrEnum


class Orientation(StrEnum):
    SQUARE="SQUARE"
    PORTRAIT="PORTRAIT"
    LANDSCAPE="LANDSCAPE"


@dataclass(frozen=True,slots=True)
class BookProfile:
    id: str
    label: str
    trim_width_in: float
    trim_height_in: float
    art_width_in: float
    art_height_in: float
    scene_count: int=40
    blank_reverse: bool=True
    bleed: bool=False

    @property
    def orientation(self):
        if self.trim_width_in==self.trim_height_in: return Orientation.SQUARE
        return Orientation.PORTRAIT if self.trim_height_in>self.trim_width_in else Orientation.LANDSCAPE

    @property
    def physical_pages(self):
        return self.scene_count*(2 if self.blank_reverse else 1)

    def validate(self):
        if min(self.trim_width_in,self.trim_height_in,self.art_width_in,self.art_height_in)<=0:
            raise ValueError("Dimensions must be positive")
        if self.art_width_in>self.trim_width_in or self.art_height_in>self.trim_height_in:
            raise ValueError("Art area cannot exceed trim size")
        if self.scene_count<=0: raise ValueError("scene_count must be positive")
        return self


COZY_SQUARE=BookProfile("cozy-square-8.5","Cozy Square 8.5 × 8.5",8.5,8.5,7.5,7.5)
CLASSIC_PORTRAIT=BookProfile("classic-portrait-8.5x11","Classic Portrait 8.5 × 11",8.5,11.0,7.5,10.0)

PROFILES={p.id:p for p in (COZY_SQUARE,CLASSIC_PORTRAIT)}


def get_profile(profile_id: str) -> BookProfile:
    try: return PROFILES[profile_id]
    except KeyError: raise ValueError(f"Unknown book profile: {profile_id}")


def custom_profile(**values) -> BookProfile:
    return BookProfile(id="custom",label="Custom",**values).validate()
