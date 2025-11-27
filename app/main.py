from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.converter import ConversionError, convert_cif_to_pdb

ALLOWED_CONTENT_TYPES = {
    "application/octet-stream",
    "application/mmcif",
    "chemical/x-mmcif",
    "chemical/x-cif",
    "application/cif",
}

ALLOWED_EXTENSIONS = {".cif", ".mmcif"}

app = FastAPI(
    title="cif2pdb",
    description="Simple service that converts mmCIF files to PDB.",
    version="0.1.0",
)


async def read_upload(file: UploadFile) -> bytes:
    """Read the uploaded file contents and return raw bytes."""
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    return data


@app.post(
    "/convert",
    summary="Convert mmCIF to PDB",
    response_description="Converted PDB file",
)
async def convert_endpoint(
    file: Annotated[UploadFile, File(description="mmCIF file")],
    cif_bytes: bytes = Depends(read_upload),
) -> StreamingResponse:
    content_type = (file.content_type or "").lower()
    file_suffix = Path(file.filename or "").suffix.lower()

    if content_type not in ALLOWED_CONTENT_TYPES and file_suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Please upload a valid mmCIF file.")

    try:
        pdb_bytes = convert_cif_to_pdb(cif_bytes)
    except ConversionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filename = file.filename or "converted"
    stem = filename.rsplit(".", 1)[0]
    output_name = f"{stem}.pdb"

    return StreamingResponse(
        BytesIO(pdb_bytes),
        media_type="chemical/x-pdb",
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )


@app.get("/health", summary="Health check")
async def health() -> dict[str, str]:
    return {"status": "ok"}

