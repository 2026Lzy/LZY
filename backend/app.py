from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import fault, rul, maintenance

# 自动创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="机械设备故障预测与运维决策系统", version="1.0")

# 跨域配置，前端可直接访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(fault.router)
app.include_router(rul.router)
app.include_router(maintenance.router)

@app.get("/")
def health_check():
    return {"system": "机械设备故障预测与运维决策系统", "status": "运行正常", "version": "1.0"}

