"""
FDF Layout Definitions
======================
Define las coordenadas relativas de los slots de fotos para los templates de FDF.
"""

# Mapeo de slots por template de FDF
# Las coordenadas son porcentuales (0.0 a 1.0) relativas al canvas
FDF_LAYOUTS = {
    "solo_fotos_1x1": {
        "name": "Solo Fotos - 1 foto por página",
        "slots": [
            {"id": "main", "x": 0.1, "y": 0.1, "w": 0.8, "h": 0.8}
        ]
    },
    "clasico": { # Alias para compatibilidad default
        "name": "Clásico - 1 foto",
        "slots": [
             {"id": "main", "x": 0.1, "y": 0.1, "w": 0.8, "h": 0.8}
        ]
    },
    "collage_2x2": {
        "name": "Collage - 4 fotos",
        "slots": [
            {"id": "top_left", "x": 0.05, "y": 0.05, "w": 0.45, "h": 0.45},
            {"id": "top_right", "x": 0.5, "y": 0.05, "w": 0.45, "h": 0.45},
            {"id": "bottom_left", "x": 0.05, "y": 0.5, "w": 0.45, "h": 0.45},
            {"id": "bottom_right", "x": 0.5, "y": 0.5, "w": 0.45, "h": 0.45}
        ]
    },
    "collage_3_horizontal": {
        "name": "Collage - 3 fotos horizontal",
        "slots": [
            {"id": "left", "x": 0.02, "y": 0.1, "w": 0.32, "h": 0.8},
            {"id": "center", "x": 0.34, "y": 0.1, "w": 0.32, "h": 0.8},
            {"id": "right", "x": 0.66, "y": 0.1, "w": 0.32, "h": 0.8}
        ]
    },
    "featured_with_thumbnails": {
        "name": "1 grande + 3 miniaturas",
        "slots": [
            {"id": "featured", "x": 0.05, "y": 0.05, "w": 0.6, "h": 0.9},
            {"id": "thumb_1", "x": 0.68, "y": 0.05, "w": 0.28, "h": 0.28},
            {"id": "thumb_2", "x": 0.68, "y": 0.36, "w": 0.28, "h": 0.28},
            {"id": "thumb_3", "x": 0.68, "y": 0.67, "w": 0.28, "h": 0.28}
        ]
    }
}


def get_slot_info(layout_name: str, slot_id: str) -> dict:
    """Obtiene información de un slot específico"""
    if layout_name not in FDF_LAYOUTS:
        # Fallback a clasico si no existe
        if layout_name == "default":
             return FDF_LAYOUTS["clasico"]["slots"][0]
        raise ValueError(f"Layout '{layout_name}' no encontrado")
    
    layout = FDF_LAYOUTS[layout_name]
    for slot in layout["slots"]:
        if slot["id"] == slot_id:
            return slot
    
    # Si piden un slot desconocido, devolvemos el primero por seguridad
    return layout["slots"][0]
