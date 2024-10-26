import streamlit as st
import time
import pandas as pd

# https://emojipedia.org/books

def main():
    st.title("Análise de documentos de patente")
    st.write("Elaboração de resumos")

    st.header("Entre com o número do pedido de patente em recurso: p.ex. 102012005032")
    numero = st.text_input("Digite aqui:")
    if texto:
        st.write("Numero: ",numero)


main()