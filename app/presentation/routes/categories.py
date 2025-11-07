# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List
# from app.infrastructure.database.connection import get_db
# from app.infrastructure.database.models import Category, User
# from app.domain.categories.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
# from app.infrastructure.auth import require_admin, get_current_user

# router = APIRouter()

# @router.post("/", response_model=CategoryResponse)
# def create_category(category: CategoryCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
#     db_category = Category(**category.model_dump())
#     db.add(db_category)
#     db.commit()
#     db.refresh(db_category)
#     return CategoryResponse.model_validate(db_category)

# @router.get("/", response_model=List[CategoryResponse])
# def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     categories = db.query(Category).offset(skip).limit(limit).all()
#     return [CategoryResponse.model_validate(cat) for cat in categories]

# @router.get("/{category_id}", response_model=CategoryResponse)
# def get_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     category = db.query(Category).filter(Category.id == category_id).first()
#     if not category:
#         raise HTTPException(status_code=404, detail="Category not found")
#     return CategoryResponse.model_validate(category)

# @router.put("/{category_id}", response_model=CategoryResponse)
# def update_category(category_id: int, category_update: CategoryUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
#     category = db.query(Category).filter(Category.id == category_id).first()
#     if not category:
#         raise HTTPException(status_code=404, detail="Category not found")
    
#     for field, value in category_update.model_dump(exclude_unset=True).items():
#         setattr(category, field, value)
    
#     db.commit()
#     db.refresh(category)
#     return CategoryResponse.model_validate(category)

# @router.delete("/{category_id}")
# def delete_category(category_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
#     category = db.query(Category).filter(Category.id == category_id).first()
#     if not category:
#         raise HTTPException(status_code=404, detail="Category not found")
    
#     db.delete(category)
#     db.commit()
#     return {"message": "Category deleted successfully"}