# FUNCIONES PARA UTILIZAR EN TODA LA APP
#************************

# FUNCION PARA FORMATEAR EL MONTO A PESOS CHILENOS
import re

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

# VALIDAR RUT CHILENO
def rut_valido(rut):
    rut = rut.strip().replace(".", "").replace("-", "").upper()

    if len(rut) < 2:
        return False

    cuerpo, dv = rut[:-1], rut[-1]

    if not cuerpo.isdigit():
        return False

    suma = 0
    factor = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1

    resto = 11 - (suma % 11)

    if resto == 11:
        dv_calculado = "0"
    elif resto == 10:
        dv_calculado = "K"
    else:
        dv_calculado = str(resto)

    return dv == dv_calculado

# VALIDAR CORREO ELECTRÓNICO
def correo_valido(correo):
    correo = correo.strip()
    return bool(
        re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo)
    )