from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.source.crud import delete_source, get_all_sources, get_source_by_id, update_source_by_id
from app.templates import templates

router = APIRouter()



# List semua source
@router.get("/source", response_class=HTMLResponse)
def list_sources(request: Request, q: Optional[str] = None):
    all_sources = get_all_sources()
    if q:
        # Filter berdasarkan nama source
        filtered_sources = [s for s in all_sources if q.lower() in s["name"].lower()]
        return templates.TemplateResponse(
            "source/list.html", {"request": request, "sources": filtered_sources, "q": q}
        )
    else:
        return templates.TemplateResponse(
            "source/list.html", {"request": request, "sources": all_sources, "q": ""}
        )


# Form edit source
@router.get("/source/edit/{source_id}", response_class=HTMLResponse)
def edit_source_form(request: Request, source_id: int):
    source = get_source_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source tidak ditemukan")
    return templates.TemplateResponse("source/edit.html", {"request": request, "source": source})


# Handler update source
@router.post("/source/edit/{source_id}")
def update_source_handler(
    request: Request, source_id: int, name: str = Form(...), q: Optional[str] = Query(None)
):
    update_source_by_id(source_id=source_id, name=name)
    redirect_url = f"/source?q={q}" if q else "/source"
    return RedirectResponse(url=redirect_url, status_code=303)


# Handler delete source
@router.post("/source/delete/{source_id}")
def delete_source_handler(request: Request, source_id: int):
    delete_source(source_id)
    return RedirectResponse(url="/source", status_code=303)
