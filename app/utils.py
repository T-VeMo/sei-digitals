#FUNCIONES PARA UTILIZAR EN TODA LA APP
#************************

#FUNCION PARA FORMATEAR EL MONTO A PESOS CHILENOS
def formato_clp(monto):
    return f"${monto:,.0f}".replace(",", ".")