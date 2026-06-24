<div align="center">
  <h1>Sistema Bancario Python</h1>
  <p><i>Un core bancario interactivo por consola (CLI) construido completamente en Python.</i></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Interfaz-CLI-4CAF50?style=for-the-badge" alt="CLI">
    <img src="https://img.shields.io/badge/Licencia-MIT-blue?style=for-the-badge" alt="License">
  </p>
</div>

---

## Acerca del Proyecto

El **Sistema Bancario Python** es una aplicación de terminal robusta y profesional diseñada para simular el ecosistema completo de un banco moderno. Utiliza bases de datos locales (`JSON`) y una arquitectura modular, permitiendo a los usuarios gestionar desde su cuenta de ahorros principal, hasta complejos productos financieros como créditos, tarjetas de crédito, e inversiones.

Con una interfaz de consola enriquecida con colores, tablas y facturas dinámicas, la experiencia de usuario se asemeja a las operaciones reales en una terminal financiera.

---

## Características Principales

*   **Multiproducto Financiero:** Crea y administra Tarjetas de Débito, Tarjetas de Crédito, y visualiza de forma separada tus ahorros y fondos de inversión.
*   **Créditos y Préstamos:** Motor inteligente para solicitar créditos (Libranza, Vivienda, Vehicular). Paga tus cuotas mensuales y visualiza facturas de liquidación automáticas al saldar tus deudas.
*   **Ahorros e Inversiones:** Constituye ahorros programados con metas dinámicas o deposita en fondos de inversión con seguimiento de rendimientos en tiempo real.
*   **Portal de Llaves (Transfiya):** Registra llaves usando tu Número de Celular, Correo Electrónico o Alias para realizar transferencias directas sin necesidad de usar números de cuenta extensos.
*   **Historial Detallado:** Tabla de movimientos codificada por colores (Ingresos en verde `+`, Egresos en rojo `-`) para una auditoría financiera perfecta.
*   **Seguridad y Validaciones:** Protección de rutas financieras mediante validación de PIN dinámico y protección de datos sensibles.

---

## Guía de Instalación y Uso

Asegúrate de tener **Python 3.7 o superior** instalado en tu computadora. Este proyecto no requiere librerías de terceros (cero dependencias externas).

### 1. Clonar el Repositorio
```bash
git clone https://github.com/TU_USUARIO/sistema-bancario-python.git
cd sistema-bancario-python
```

### 2. Ejecutar la Aplicación
Inicia la terminal interactiva ejecutando el archivo principal del sistema:
```bash
python banking_system/main.py
```

### 3. Primeros Pasos
*   Al iniciar, el sistema te preguntará si deseas **iniciar sesión** o **crear una cuenta nueva**.
*   Para iniciar desde cero, crea tu cuenta proporcionando tus datos básicos y estableciendo un **PIN de 4 dígitos**.
*   ¡Empieza a navegar por las opciones numéricas para explorar tus productos!

---

## 📂 Estructura del Proyecto

```text
sistema_bancario_Py/
├── banking_system/
│   ├── data/            # Bases de datos JSON (aisladas del repo)
│   ├── database/        # Lógica de lectura/escritura de datos
│   ├── models/          # Modelos de negocio (Account, Loan, Product, etc.)
│   ├── services/        # Lógica y validación (TransactionService, etc.)
│   ├── ui/              # Interfaz de usuario y renderizado (Menús, Colores)
│   ├── utils/           # Excepciones personalizadas
│   └── main.py          # Archivo de arranque del proyecto
├── .gitignore           # Archivos ignorados por Git
└── README.md            # Este documento
```

---

## Autor

Este proyecto fue desarrollado íntegramente por:

*   **Tomas Medina**
*   Contacto: [tom.pradamd@gmail.com](mailto:tom.pradamd@gmail.com)

---
<div align="center">
  <i>Desarrollado con lógica pura en Python 🐍</i>
</div>
