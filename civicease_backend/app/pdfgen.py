"""Tiny dependency-free PDF writer for the offline checklist (Latin-1 text only; Hindi needs a font-embedding library)."""
import textwrap


def _esc(s: str) -> str:
    s = s.encode("latin-1", "replace").decode("latin-1")
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(lines: list) -> bytes:
    wrapped = []
    for ln in lines:
        wrapped += textwrap.wrap(ln, 95) or [""]
    pages = [wrapped[i:i + 52] for i in range(0, len(wrapped), 52)] or [[]]
    n = len(pages)
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(n))
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode(),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for i, pg in enumerate(pages):
        body = "BT /F1 11 Tf 50 800 Td 14 TL\n" + "\n".join(f"({_esc(l)}) Tj T*" for l in pg) + "\nET"
        c = body.encode("latin-1")
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> "
                    f"/Contents {5 + 2 * i} 0 R >>".encode())
        objs.append(b"<< /Length %d >>\nstream\n" % len(c) + c + b"\nendstream")
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for i, o in enumerate(objs):
        offsets.append(len(out))
        out += f"{i + 1} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)
