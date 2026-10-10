# FUNCIONES PARA UTILIZAR EN TODA LA APP
#************************

# FUNCION PARA FORMATEAR EL MONTO A PESOS CHILENOS
def formato_clp(monto):
    return f"${monto:,.0f}".replace(",", ".")

# VERIFICA SI EL TELEFONO ES VALIDO Y TIENE 8 DIGITOS
def telefono_valido(telefono):
    return telefono.isdigit() and len(telefono) == 8

# NORMALIZAR RUT AL FORMATO 12345678-K
def normalizar_rut(rut):
    rut = rut.strip().replace(".", "").replace("-", "").upper()

    if len(rut) < 2:
        return rut

    return f"{rut[:-1]}-{rut[-1]}"

def rut_valido(rut):
    rut = rut.strip().replace(".", "").replace("-", "")
    if len(rut) < 2:
        return False
    cuerpo, dv = rut[:-1], rut[-1].upper()
    if not cuerpo.isdigit():
        return False
    suma = sum(int(c) * (2 + i % 6) for i, c in enumerate(reversed(cuerpo)))
    dv_calculado = str((11 - (suma % 11)) % 11)
    if dv_calculado == "10":
        dv_calculado = "K"
    return dv == dv_calculado