from typing import List, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.source.crud import (
    create_source,
    delete_source,
    get_all_sources,
    get_source_by_id,
    update_source_by_id,
)
from app.templates import templates

router = APIRouter()


# Sidebar dinamis
def get_sidebar_sources():
    return get_all_sources()


# LIST / SEARCH SOURCES
@router.get("/source", response_class=HTMLResponse)
def list_sources(request: Request, q: Optional[str] = None):
    all_sources = get_all_sources()
    if q:
        filtered_sources = [s for s in all_sources if q.lower() in s["name"].lower()]
    else:
        filtered_sources = all_sources

    return templates.TemplateResponse(
        "source/list.html",
        {
            "request": request,
            "sources": filtered_sources,
            "q": q or "",
            "sources_sidebar": get_sidebar_sources(),
        },
    )


# ADD SOURCE FORM
@router.get("/source/add", response_class=HTMLResponse)
def add_source_form(request: Request):
    return templates.TemplateResponse(
        "source/add.html", {"request": request, "sources_sidebar": get_sidebar_sources()}
    )


# CREATE SOURCE
@router.post("/source/add")
def create_source_handler(request: Request, name: str = Form(...)):
    if not name.strip():
        raise HTTPException(status_code=400, detail="Nama source tidak boleh kosong")
    create_source({"name": name.strip()})
    return RedirectResponse(url="/source", status_code=303)


# EDIT SOURCE FORM
@router.get("/source/edit/{source_id}", response_class=HTMLResponse)
def edit_source_form(request: Request, source_id: int):
    source = get_source_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source tidak ditemukan")
    return templates.TemplateResponse(
        "source/edit.html",
        {"request": request, "source": source, "sources_sidebar": get_sidebar_sources()},
    )


# UPDATE SOURCE
@router.post("/source/edit/{source_id}")
def update_source_handler(
    request: Request, source_id: int, name: str = Form(...), q: Optional[str] = Query(None)
):
    source = get_source_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source tidak ditemukan")

    update_source_by_id(source_id=source_id, name=name)
    query_string = f"?{urlencode({'q': q})}" if q else ""
    return RedirectResponse(url=f"/source{query_string}", status_code=303)


# DELETE SOURCE
@router.post("/source/delete/{source_id}")
def delete_source_handler(request: Request, source_id: int):
    source = get_source_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source tidak ditemukan")
    delete_source(source_id)
    return RedirectResponse(url="/source", status_code=303)
