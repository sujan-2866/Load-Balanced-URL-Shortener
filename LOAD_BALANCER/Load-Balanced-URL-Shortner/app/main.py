from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models, utils
from .models import URL, get_db
from .config import BASE_URL
from pydantic import BaseModel
import logging
import os

# Initialize FastAPI
app = FastAPI(title="URL Shortener Service")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates configuration
templates = Jinja2Templates(directory="app/templates")

# Create database tables on startup
@app.on_event("startup")
async def startup():
    models.create_tables()
    logger.info("Application started and database tables created")

# Pydantic model for URL creation requests
class URLCreate(BaseModel):
    url: str

# Pydantic model for URL responses
class URLResponse(BaseModel):
    original_url: str
    short_url: str
    short_url_link: str

# Frontend routes
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    logger.info(f"Pod {os.getenv('HOSTNAME')} serving frontend index page to {request.client.host}")
    return templates.TemplateResponse("index.html", {"request": request})

# API routes
@app.post("/shorten/", response_model=URLResponse)
def create_short_url(url_data: URLCreate, db: Session = Depends(get_db)):
    logger.info(f"Pod {os.getenv('HOSTNAME')} received shorten request for URL: {url_data.url}")
    # Check if the URL already exists in the database
    existing_url = db.query(URL).filter(URL.original_url == url_data.url).first()
    
    if existing_url:
        logger.info(f"Pod {os.getenv('HOSTNAME')} found existing short URL: {existing_url.short_url}")
        return {
            "original_url": existing_url.original_url,
            "short_url": existing_url.short_url,
            "short_url_link": f"{BASE_URL}/{existing_url.short_url}"
        }
    
    # If URL doesn't exist, generate a new short URL
    short_id = utils.generate_short_url()
    
    # Create a new URL entry
    db_url = URL(
        short_url=short_id,
        original_url=url_data.url
    )
    
    # Save to database
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    logger.info(f"Pod {os.getenv('HOSTNAME')} created new short URL: {db_url.short_url}")
    return {
        "original_url": db_url.original_url,
        "short_url": db_url.short_url,
        "short_url_link": f"{BASE_URL}/{db_url.short_url}"
    }

@app.put("/update/{short_url}", response_model=URLResponse)
def update_url(short_url: str, url_data: URLCreate, db: Session = Depends(get_db)):
    logger.info(f"Pod {os.getenv('HOSTNAME')} received update request for short URL: {short_url}")
    # Find the URL entry by short_url
    db_url = db.query(URL).filter(URL.short_url == short_url).first()
    
    if db_url is None:
        logger.warning(f"Pod {os.getenv('HOSTNAME')} could not find short URL: {short_url}")
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Update the original URL
    db_url.original_url = url_data.url
    db.commit()
    db.refresh(db_url)
    
    logger.info(f"Pod {os.getenv('HOSTNAME')} updated short URL: {short_url} to {url_data.url}")
    return {
        "original_url": db_url.original_url,
        "short_url": db_url.short_url,
        "short_url_link": f"{BASE_URL}/{db_url.short_url}"
    }

@app.delete("/delete/{short_url}")
def delete_short_url(short_url: str, db: Session = Depends(get_db)):
    logger.info(f"Pod {os.getenv('HOSTNAME')} received delete request for short URL: {short_url}")
    # Lookup the URL entry by short URL
    db_url = db.query(URL).filter(URL.short_url == short_url).first()
    
    # If URL doesn't exist, raise 404
    if db_url is None:
        logger.warning(f"Pod {os.getenv('HOSTNAME')} could not find short URL: {short_url}")
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Delete the URL entry
    db.delete(db_url)
    db.commit()
    
    logger.info(f"Pod {os.getenv('HOSTNAME')} deleted short URL: {short_url}")
    return {"detail": f"URL with short URL {short_url} has been deleted"}

@app.get("/urls/", response_model=list[URLResponse])
def get_all_urls(db: Session = Depends(get_db)):
    logger.info(f"Pod {os.getenv('HOSTNAME')} received request to list all URLs")
    urls = db.query(URL).all()
    response = [
        {
            "original_url": url.original_url,
            "short_url": url.short_url,
            "short_url_link": f"{BASE_URL}/{url.short_url}"
        } for url in urls
    ]
    logger.info(f"Pod {os.getenv('HOSTNAME')} returned {len(response)} URLs")
    return response

@app.get("/{short_url}", response_class=RedirectResponse)
def redirect_to_original(short_url: str, db: Session = Depends(get_db)):
    logger.info(f"Pod {os.getenv('HOSTNAME')} received redirect request for short URL: {short_url}")
    
    # Skip redirection for static files and API endpoints
    if short_url in ["static", "shorten", "update", "delete", "urls"]:
        logger.warning(f"Pod {os.getenv('HOSTNAME')} blocked reserved path: {short_url}")
        raise HTTPException(status_code=404, detail="URL not found")
        
    # Lookup the original URL
    db_url = db.query(URL).filter(URL.short_url == short_url).first()
    
    # If URL doesn't exist, raise 404
    if db_url is None:
        logger.warning(f"Pod {os.getenv('HOSTNAME')} could not find short URL: {short_url}")
        raise HTTPException(status_code=404, detail="URL not found")
    
    logger.info(f"Pod {os.getenv('HOSTNAME')} redirecting {short_url} to {db_url.original_url}")
    # Redirect to the original URL
    return RedirectResponse(url=db_url.original_url)