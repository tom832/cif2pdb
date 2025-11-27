from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Final

import pymol2


class ConversionError(RuntimeError):
    """Raised when PyMOL cannot convert an mmCIF file to PDB."""


OBJECT_NAME: Final[str] = "cif_model"


def convert_cif_to_pdb(cif_bytes: bytes) -> bytes:
    """
    Convert mmCIF contents to PDB format via PyMOL and return bytes.

    The uploaded binary is written to a temporary file, loaded by PyMOL,
    and exported as PDB.
    """
    if not cif_bytes.strip():
        raise ConversionError("Provided mmCIF content is empty; conversion aborted.")

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        cif_path = temp_dir / "input.cif"
        pdb_path = temp_dir / "output.pdb"

        cif_path.write_bytes(cif_bytes)

        try:
            with pymol2.PyMOL() as pymol:
                cmd = pymol.cmd
                cmd.reinitialize()
                cmd.load(str(cif_path), OBJECT_NAME)
                cmd.save(str(pdb_path), OBJECT_NAME, state=1, format="pdb")
        except Exception as exc:  # noqa: BLE001
            raise ConversionError("PyMOL failed to convert the mmCIF file.") from exc

        if not pdb_path.exists():
            raise ConversionError("PDB output file was not generated.")

        return pdb_path.read_bytes()

