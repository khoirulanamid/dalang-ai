# Wiku 3D & Blender Standards (Knowledge-First Execution)

## 1. Blender bpy Scripting Standards
- Always use `bpy.data` and `bmesh` rather than `bpy.ops` where possible for stability.
- Knowledge-First: verify API and dimensions before generating 3D operations.
- Export formats: GLB/GLTF with draco compression or clean mesh buffers.
