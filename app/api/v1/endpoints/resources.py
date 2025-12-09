from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.core.response import success_response
from app.core.logging_config import get_logger
from app.models.resource import Resource, ResourceType, ResourceStatus
from app.schemas.resource import ResourceCreate, ResourceResponse, ResourceUpdate, ResourceListResponse

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_resource(resource_data: ResourceCreate, db: Session = Depends(get_db)):
    logger.info(
        f"Creating resource: {resource_data.title}",
        extra={"extra_data": {"type": str(resource_data.type), "school_id": str(resource_data.school_id) if resource_data.school_id else None}}
    )
    
    if resource_data.type == ResourceType.VIDEO and not resource_data.video_url:
        logger.warning("Resource creation failed - video_url required")
        raise HTTPException(status_code=400, detail="video_url required for videos")

    if resource_data.type == ResourceType.AUDIO and not resource_data.audio_url:
        logger.warning("Resource creation failed - audio_url required")
        raise HTTPException(status_code=400, detail="audio_url required for audio")

    if resource_data.type == ResourceType.ARTICLE and not resource_data.article_url:
        logger.warning("Resource creation failed - article_url required")
        raise HTTPException(status_code=400, detail="article_url required for articles")

    resource = Resource(**resource_data.dict())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    logger.info(f"Resource created successfully", extra={"extra_data": {"resource_id": str(resource.resource_id)}})
    return success_response(resource)

@router.get("")
async def list_resources(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[UUID] = None,
    type: Optional[ResourceType] = None,
    status: Optional[ResourceStatus] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    target_audience: Optional[str] = None,
    author_id: Optional[UUID] = None,
    search: Optional[str] = None,
    include_global: bool = True,
    db: Session = Depends(get_db)
):
    logger.debug(
        "Listing resources",
        extra={"extra_data": {"school_id": str(school_id) if school_id else None, "type": str(type) if type else None, "category": category}}
    )
    
    query = db.query(Resource)

    if school_id:
        if include_global:
            query = query.filter(or_(Resource.school_id == school_id, Resource.school_id.is_(None)))
        else:
            query = query.filter(Resource.school_id == school_id)
    elif not include_global:
        query = query.filter(Resource.school_id.isnot(None))

    if type:
        query = query.filter(Resource.type == type)

    if status:
        query = query.filter(Resource.status == status)
    else:
        query = query.filter(Resource.status == ResourceStatus.PUBLISHED)

    if category:
        query = query.filter(Resource.category == category)

    if tag:
        query = query.filter(Resource.tags.contains([tag]))

    if target_audience:
        query = query.filter(Resource.target_audience.contains([target_audience]))

    if author_id:
        query = query.filter(Resource.author_id == author_id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(Resource.title.ilike(pattern), Resource.description.ilike(pattern)))

    query = query.order_by(Resource.posted_date.desc())
    resources = query.offset(skip).limit(limit).all()
    logger.debug(f"Found {len(resources)} resources")
    return success_response(resources)

@router.get("/{resource_id}")
async def get_resource(resource_id: UUID, increment_view: bool = True, db: Session = Depends(get_db)):
    logger.debug(f"Fetching resource: {resource_id}")
    
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        logger.warning(f"Resource not found: {resource_id}")
        raise HTTPException(status_code=404, detail="Resource not found")

    if increment_view:
        resource.view_count += 1
        db.commit()
        db.refresh(resource)

    return success_response(resource)

@router.patch("/{resource_id}")
async def update_resource(resource_id: UUID, resource_update: ResourceUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating resource: {resource_id}")
    
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        logger.warning(f"Resource update failed - not found: {resource_id}")
        raise HTTPException(status_code=404, detail="Resource not found")

    for field, value in resource_update.dict(exclude_unset=True).items():
        setattr(resource, field, value)

    resource.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(resource)
    
    logger.info(f"Resource updated successfully", extra={"extra_data": {"resource_id": str(resource_id)}})
    return success_response(resource)

@router.delete("/{resource_id}")
async def delete_resource(resource_id: UUID, db: Session = Depends(get_db)):
    logger.info(f"Deleting resource: {resource_id}")
    
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        logger.warning(f"Resource deletion failed - not found: {resource_id}")
        raise HTTPException(status_code=404, detail="Resource not found")

    db.delete(resource)
    db.commit()
    
    logger.info(f"Resource deleted successfully", extra={"extra_data": {"resource_id": str(resource_id)}})
    return success_response({"message": "Resource deleted successfully", "resource_id": str(resource_id)})

@router.get("/categories/list")
async def list_categories(school_id: Optional[UUID] = None, include_global: bool = True, db: Session = Depends(get_db)):
    query = db.query(Resource.category, func.count(Resource.resource_id).label('count'))

    if school_id:
        if include_global:
            query = query.filter(or_(Resource.school_id == school_id, Resource.school_id.is_(None)))
        else:
            query = query.filter(Resource.school_id == school_id)

    query = query.filter(Resource.status == ResourceStatus.PUBLISHED, Resource.category.isnot(None))
    query = query.group_by(Resource.category).order_by(func.count(Resource.resource_id).desc())

    return success_response([{"category": cat, "count": cnt} for cat, cnt in query.all()])

@router.get("/tags/list")
async def list_tags(school_id: Optional[UUID] = None, include_global: bool = True, db: Session = Depends(get_db)):
    query = db.query(Resource)

    if school_id:
        if include_global:
            query = query.filter(or_(Resource.school_id == school_id, Resource.school_id.is_(None)))
        else:
            query = query.filter(Resource.school_id == school_id)

    query = query.filter(Resource.status == ResourceStatus.PUBLISHED, Resource.tags.isnot(None))
    resources = query.all()

    tag_counts = {}
    for resource in resources:
        if resource.tags:
            for tag in resource.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return success_response([{"tag": tag, "count": count} for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)])

@router.get("/stats/overview")
async def get_resources_stats(school_id: Optional[UUID] = None, include_global: bool = True, db: Session = Depends(get_db)):
    query = db.query(Resource)

    if school_id:
        if include_global:
            query = query.filter(or_(Resource.school_id == school_id, Resource.school_id.is_(None)))
        else:
            query = query.filter(Resource.school_id == school_id)

    query = query.filter(Resource.status == ResourceStatus.PUBLISHED)
    resources = query.all()

    total = len(resources)
    videos = sum(1 for r in resources if r.type == ResourceType.VIDEO)
    audio = sum(1 for r in resources if r.type == ResourceType.AUDIO)
    articles = sum(1 for r in resources if r.type == ResourceType.ARTICLE)
    views = sum(r.view_count for r in resources)

    return success_response({
        "total_resources": total,
        "by_type": {"videos": videos, "audio": audio, "articles": articles},
        "total_views": views,
        "average_views": round(views / total, 2) if total > 0 else 0
    })
