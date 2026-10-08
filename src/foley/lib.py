"""Top level entry point for the Foley library."""

from pathlib import Path

from foley.capabilities.audition.audition import audition as audition
from foley.capabilities.create.create import create as create
from foley.capabilities.doctor.doctor import doctor as doctor
from foley.capabilities.export.export import export as export
from foley.capabilities.inspect.inspect import inspect as inspect
from foley.capabilities.list.list import list_sounds as list_sounds
from foley.capabilities.models.models import models as models
from foley.capabilities.recipe.recipe import RECIPES as RECIPES
from foley.capabilities.recipe.recipe import recipe as recipe
from foley.capabilities.render.render import render as render
from foley.capabilities.revise.revise import revise as revise
from foley.capabilities.variants.variants import variants as variants
from foley.core import manifest
from foley.core import skill as skill_module
from foley.schemas import Manifest


def load_manifest() -> Manifest:
    """The tool's manifest as structured data, read from the SMART_TOOL.md shipped inside the package."""
    return manifest.load_manifest()


def skill(capability: str | None = None) -> str:
    """The tool's skill, or the named capability's own skill, wrapped so a reader knows where the tool's files are."""
    return skill_module.skill(capability)


def skill_directory() -> Path:
    """The installed package root, where the files the skill names can be read."""
    return skill_module.skill_directory()


def skill_resources() -> list[str]:
    """The files the skill lists, as paths relative to the skill directory. Every one ships inside the package."""
    return skill_module.skill_resources()


def capability_skill_resources(capability: str) -> list[str]:
    """The files that capability's skill lists, as paths relative to the skill directory."""
    return skill_module.capability_skill_resources(capability)


def repository_url() -> str | None:
    """The tool's canonical source, from the package metadata, or None when the package declares none."""
    return skill_module.repository_url()
