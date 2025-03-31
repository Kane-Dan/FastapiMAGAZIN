from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import jwt
from src.config import ALGORITHM, SECRET_KEY
from src.auth.routers import router as auth_router
from src.products.routers import router as product_router
from src.categories.routers import router as category_router
from src.admin.routers import router as admin_router
app = FastAPI() 


app.include_router(auth_router,prefix="/Users", tags = ["Auth"])
app.include_router(product_router,prefix="/Products", tags = ["Products"])
app.include_router(category_router,prefix="/Categories",tags = ["Categories"])
app.include_router(admin_router,prefix="/Admin",tags = ["Admin"])




# mid
@app.middleware("http")
async def verify_access_token(request: Request, call_next):
    
    if "/Admin" in request.url.path:
        
        access_token = request.cookies.get("access_token")

        if not access_token or not access_token.startswith("Bearer"):
            return JSONResponse(
                status_code=401,
                content={"message": "Authentication required for paths containing '/admin'."},
            )

        # Извлекаем сам токен
        token = access_token.split(" ")[1]

        try:
            # Декодируем токен
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_role = payload.get("role")

            # Проверяем роль
            if user_role not in ["admin", "worker"]:
                return JSONResponse(
                    status_code=403,
                    content={"message": "Access denied. Admin role required."},
                )
        except jwt.PyJWTError:
            return JSONResponse(
                status_code=401,
                content={"message": "Invalid token."},
            )
    
    
    response = await call_next(request)
    return response