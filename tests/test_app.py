from fastapi.testclient import TestClient

from app import main
from app.converter import ConversionError


client = TestClient(main.app)


def test_convert_success(monkeypatch):
    sample_data = b"data_demo\n# sample cif content"

    def fake_convert(data: bytes) -> bytes:
        assert data == sample_data
        return b"HEADER    DUMMY PDB\nEND\n"

    monkeypatch.setattr(main, "convert_cif_to_pdb", fake_convert)

    response = client.post(
        "/convert",
        files={"file": ("demo.cif", sample_data, "application/mmcif")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "chemical/x-pdb"
    assert response.headers["content-disposition"] == 'attachment; filename="demo.pdb"'
    assert response.content.startswith(b"HEADER")


def test_convert_failure(monkeypatch):
    def fake_convert(_: bytes) -> bytes:
        raise ConversionError("Conversion failed")

    monkeypatch.setattr(main, "convert_cif_to_pdb", fake_convert)

    response = client.post(
        "/convert",
        files={"file": ("demo.cif", b"data", "application/mmcif")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Conversion failed"


def test_invalid_content_type():
    response = client.post(
        "/convert",
        files={"file": ("demo.txt", b"data", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Please upload a valid mmCIF file."

