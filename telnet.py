import asyncio
import telnetlib3

# Telnet mínimo y rápido para Cisco IOS: entra a enable, desactiva paginación
async def main():
    host = "10.10.20.1"      # Cambia si tu equipo usa otra IP
    port = 23                 # Cisco Telnet por defecto
    username = "admin"       # Ajusta a tus credenciales
    password = "admin"       # Se usa también como enable si aplica

    reader, writer = await telnetlib3.open_connection(host=host, port=port, encoding="ascii")

    # Helper: esperar prompt ('#' preferido) o '>' si no hay privilegios
    async def wait_prompt(timeout=6):
        try:
            data = await asyncio.wait_for(reader.readuntil(b"#"), timeout=timeout)
            return "#", data
        except asyncio.TimeoutError:
            data = await asyncio.wait_for(reader.readuntil(b">"), timeout=timeout)
            return ">", data

    # Disparar banner y negociar login de forma tolerante
    writer.write("\r\n")
    try:
        await asyncio.wait_for(reader.readuntil(b"Username:"), timeout=6)
        writer.write(username + "\r\n")
        try:
            await asyncio.wait_for(reader.readuntil(b"Password:"), timeout=5)
            writer.write(password + "\r\n")
        except asyncio.TimeoutError:
            pass
    except asyncio.TimeoutError:
        try:
            await asyncio.wait_for(reader.readuntil(b"Password:"), timeout=5)
            writer.write(password + "\r\n")
        except asyncio.TimeoutError:
            pass

    prompt, _ = await wait_prompt(timeout=8)

    # Intentar enable si estamos en modo usuario ('>')
    if prompt == ">":
        writer.write("enable\r\n")
        try:
            await asyncio.wait_for(reader.readuntil(b"Password:"), timeout=4)
            writer.write(password + "\r\n")
        except asyncio.TimeoutError:
            pass
        prompt, _ = await wait_prompt(timeout=8)

    # Desactivar paginación para que show running-config no pagine
    writer.write("terminal length 0\r\n")
    await wait_prompt(timeout=4)

    # Ejecutar comandos y leer hasta el prompt '#'
    async def run_cmd(cmd: str, timeout: int):
        writer.write(cmd + "\r\n")
        out = await asyncio.wait_for(reader.readuntil(b"#"), timeout=timeout)
        text = out.decode("ascii", "ignore")
        # Quitar eco del comando
        marker = cmd + "\r\n"
        if marker in text:
            text = text.split(marker, 1)[-1]
        # Quitar la última línea si es el prompt
        lines = text.splitlines()
        if lines and lines[-1].strip().endswith('#'):
            lines = lines[:-1]
        return "\n".join(lines).strip()

    print("--- show version ---")
    print(await run_cmd("show version", timeout=8))

    print("--- show ip interface brief ---")
    print(await run_cmd("show ip interface brief", timeout=8))

    print("--- show running-config ---")
    # running-config puede ser largo, dar un poco más de tiempo
    print(await run_cmd("show running-config", timeout=20))

    writer.write("exit\r\n")
    writer.close()

if __name__ == "__main__":
    asyncio.run(main())