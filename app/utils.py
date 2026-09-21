# FUNCIONES PARA UTILIZAR EN TODA LA APP
#************************

# FUNCION PARA FORMATEAR EL MONTO A PESOS CHILENOS
def formato_clp(monto):
    return f"${monto:,.0f}".replace(",", ".")

# VERIFICA SI EL TELEFONO ES VALIDO Y TIENE 8 DIGITOS
def telefono_valido(telefono):
    return telefono.isdigit() and len(telefono) == 8