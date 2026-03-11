"""
Script para probar WebSocket + Notificaciones
Ejecutar: python test_websocket.py
"""
import asyncio
import json
import io
import httpx
import websockets

BASE_URL = "http://localhost:8000/api/v1"
WS_URL = "ws://localhost:8000/ws"


def create_fake_image() -> bytes:
    """Crea un PNG mínimo válido (1x1 pixel rojo)"""
    import struct
    import zlib

    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc

    signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    raw_data = b'\x00\xff\x00\x00'  # filter byte + RGB
    idat_data = zlib.compress(raw_data)

    return signature + chunk(b'IHDR', ihdr_data) + chunk(b'IDAT', idat_data) + chunk(b'IEND', b'')


async def main():
    print("=" * 60)
    print("🧪 PRUEBA DE WEBSOCKET + NOTIFICACIONES")
    print("=" * 60)

    async with httpx.AsyncClient() as client:

        # ── 1. Registrar 2 usuarios ──────────────────────────
        print("\n📝 Registrando usuario A (dueño del pin)...")
        resp_a = await client.post(f"{BASE_URL}/auth/register", json={
            "username": "user_owner_ws6",
            "email": "owner_ws6@test.com",
            "password": "Test1234!",
            "full_name": "Owner WS Test",
        })
        print(f"   Status: {resp_a.status_code}")

        print("\n📝 Registrando usuario B (el que interactúa)...")
        resp_b = await client.post(f"{BASE_URL}/auth/register", json={
            "username": "user_actor_ws6",
            "email": "actor_ws6@test.com",
            "password": "Test1234!",
            "full_name": "Actor WS Test",
        })
        print(f"   Status: {resp_b.status_code}")

        # ── 2. Login ambos ────────────────────────────────────
        print("\n🔐 Login usuario A...")
        login_a = await client.post(f"{BASE_URL}/auth/login", json={
            "identity": "owner_ws6@test.com",
            "password": "Test1234!",
        })
        login_a_data = login_a.json()
        token_a = login_a_data.get("token", "")
        user_a_id = login_a_data.get("user", {}).get("id", "")
        print(f"   ✅ Token A: {token_a[:30]}...")
        print(f"   ✅ User A ID: {user_a_id}")

        print("\n🔐 Login usuario B...")
        login_b = await client.post(f"{BASE_URL}/auth/login", json={
            "identity": "actor_ws6@test.com",
            "password": "Test1234!",
        })
        login_b_data = login_b.json()
        token_b = login_b_data.get("token", "")
        user_b_id = login_b_data.get("user", {}).get("id", "")
        print(f"   ✅ Token B: {token_b[:30]}...")
        print(f"   ✅ User B ID: {user_b_id}")

        if not token_a or not token_b or not user_a_id or not user_b_id:
            print("\n❌ Faltan datos. Abortando.")
            return

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # ── 3. Usuario A crea un pin (multipart/form-data) ───
        print("\n📌 Usuario A crea un pin (multipart con imagen)...")

        fake_image = create_fake_image()

        pin_resp = await client.post(
            f"{BASE_URL}/pins",
            headers=headers_a,
            files={
                "image": ("test_outfit.png", io.BytesIO(fake_image), "image/png"),
            },
            data={
                "title": "Outfit de prueba WebSocket",
                "category": "outfit_completo",
                "description": "Pin para probar notificaciones",
                "season": "primavera",
                "price_range": "bajo_500",
                "is_private": "false",
            },
        )

        print(f"   Pin response: {pin_resp.status_code} {pin_resp.text[:400]}")

        if pin_resp.status_code in (200, 201):
            pin_data = pin_resp.json()
            pin_id = pin_data.get("id", "") or pin_data.get("pin_id", "")
            print(f"   ✅ Pin creado: {pin_id}")
        else:
            print(f"   ❌ Error creando pin")
            return

        # ── 4. Conectar WebSocket del usuario A ──────────────
        print(f"\n🔌 Conectando WebSocket del usuario A...")

        try:
            async with websockets.connect(f"{WS_URL}?token={token_a}") as ws_a:
                print("   ✅ WebSocket conectado!")

                try:
                    welcome = await asyncio.wait_for(ws_a.recv(), timeout=3)
                    print(f"   📨 Bienvenida: {welcome}")
                except asyncio.TimeoutError:
                    print("   ℹ️ Sin mensaje de bienvenida (OK)")

                # ── 5. FOLLOW ────────────────────────────────
                print(f"\n👤 Usuario B sigue a usuario A ({user_a_id})...")
                follow_resp = await client.post(f"{BASE_URL}/follows", json={
                    "user_id": user_a_id,
                }, headers=headers_b)
                print(f"   Response: {follow_resp.status_code} {follow_resp.text[:200]}")

                try:
                    msg = await asyncio.wait_for(ws_a.recv(), timeout=5)
                    data = json.loads(msg)
                    print(f"   🔔 NOTIFICACIÓN FOLLOW:")
                    print(f"      {json.dumps(data, indent=6, ensure_ascii=False)}")
                except asyncio.TimeoutError:
                    print("   ⚠️ Sin notificación de follow (timeout)")

                # ── 6. LIKE ──────────────────────────────────
                print(f"\n❤️ Usuario B da like al pin de A ({pin_id})...")
                like_resp = await client.post(f"{BASE_URL}/likes", json={
                    "pin_id": pin_id,
                }, headers=headers_b)
                print(f"   Response: {like_resp.status_code} {like_resp.text[:200]}")

                try:
                    msg = await asyncio.wait_for(ws_a.recv(), timeout=5)
                    data = json.loads(msg)
                    print(f"   🔔 NOTIFICACIÓN LIKE:")
                    print(f"      {json.dumps(data, indent=6, ensure_ascii=False)}")
                except asyncio.TimeoutError:
                    print("   ⚠️ Sin notificación de like (timeout)")

                # ── 7. COMMENT ───────────────────────────────
                print(f"\n💬 Usuario B comenta en el pin de A...")
                comment_resp = await client.post(f"{BASE_URL}/comments", json={
                    "pin_id": pin_id,
                    "text": "Me encanta este outfit!",
                }, headers=headers_b)
                print(f"   Response: {comment_resp.status_code} {comment_resp.text[:200]}")

                try:
                    msg = await asyncio.wait_for(ws_a.recv(), timeout=5)
                    data = json.loads(msg)
                    print(f"   🔔 NOTIFICACIÓN COMMENT:")
                    print(f"      {json.dumps(data, indent=6, ensure_ascii=False)}")
                except asyncio.TimeoutError:
                    print("   ⚠️ Sin notificación de comment (timeout)")

                print("\n" + "=" * 60)
                print("✅ PRUEBA COMPLETADA")
                print("=" * 60)

        except Exception as e:
            print(f"   ❌ Error WebSocket: {e}")
            print("   💡 Asegúrate de que el servidor esté corriendo: python run.py")


if __name__ == "__main__":
    asyncio.run(main())