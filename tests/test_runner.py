"""
🧪 Test Runner y Scripts de Testing

Scripts para ejecutar todos los tests y generar reportes
"""

import subprocess
import sys
import os
from pathlib import Path


def run_all_tests():
    """Ejecuta todos los tests con pytest"""

    print("🧪 EJECUTANDO SUITE COMPLETA DE TESTS")
    print("=" * 60)

    # Cambiar al directorio de la aplicación
    os.chdir(Path(__file__).parent.parent.parent)

    # Comando pytest con opciones útiles
    cmd = [
        "uv",
        "run",
        "pytest",
        "app/tests/",
        "-v",  # Verbose
        "--tb=short",  # Traceback corto
        "--strict-markers",  # Strict markers
        "--disable-warnings",  # Deshabilitar warnings de terceros
        "-x",  # Parar en primer fallo (opcional)
    ]

    print(f"📋 Ejecutando: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False


def run_tests_with_coverage():
    """Ejecuta tests con coverage"""

    print("🧪 EJECUTANDO TESTS CON COVERAGE")
    print("=" * 60)

    os.chdir(Path(__file__).parent.parent.parent)

    cmd = [
        "uv",
        "run",
        "pytest",
        "app/tests/",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v",
    ]

    print(f"📋 Ejecutando: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode == 0:
            print()
            print("📊 Coverage report generado en: htmlcov/index.html")

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando tests con coverage: {e}")
        return False


def run_specific_test_file(test_file):
    """Ejecuta un archivo específico de tests"""

    print(f"🧪 EJECUTANDO TEST: {test_file}")
    print("=" * 60)

    os.chdir(Path(__file__).parent.parent.parent)

    cmd = ["uv", "run", "pytest", f"app/tests/{test_file}", "-v", "--tb=short"]

    print(f"📋 Ejecutando: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando test {test_file}: {e}")
        return False


def run_performance_tests():
    """Ejecuta solo tests de performance"""

    print("🧪 EJECUTANDO TESTS DE PERFORMANCE")
    print("=" * 60)

    os.chdir(Path(__file__).parent.parent.parent)

    cmd = [
        "uv",
        "run",
        "pytest",
        "app/tests/test_integration.py::TestPerformanceWorkflow",
        "-v",
        "--tb=short",
    ]

    print(f"📋 Ejecutando: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando tests de performance: {e}")
        return False


def check_test_dependencies():
    """Verifica que las dependencias de testing estén instaladas"""

    print("🔍 VERIFICANDO DEPENDENCIAS DE TESTING")
    print("=" * 60)

    dependencies = ["pytest", "pytest-cov", "httpx"]  # httpx para TestClient

    missing = []

    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - FALTANTE")
            missing.append(dep)

    if missing:
        print(f"\n⚠️ Dependencias faltantes: {', '.join(missing)}")
        print(f"💡 Instalar con: uv add {' '.join(missing)}")
        return False
    else:
        print("\n✅ Todas las dependencias están instaladas")
        return True


def show_test_structure():
    """Muestra la estructura de tests disponibles"""

    print("📁 ESTRUCTURA DE TESTS")
    print("=" * 60)

    test_files = [
        ("conftest.py", "Configuración común y fixtures"),
        ("test_schemas.py", "Tests para modelos Pydantic/SQLModel"),
        ("test_services.py", "Tests para lógica de negocio"),
        ("test_endpoints.py", "Tests para API endpoints"),
        ("test_utils.py", "Tests para funciones de utilidad"),
        ("test_integration.py", "Tests de integración end-to-end"),
        ("test_runner.py", "Este archivo - runner de tests"),
    ]

    for filename, description in test_files:
        print(f"📄 {filename:<20} - {description}")

    print("\n🎯 COMANDOS ÚTILES:")
    print("• Todos los tests:     uv run python app/tests/test_runner.py")
    print("• Con coverage:        uv run python app/tests/test_runner.py --coverage")
    print(
        "• Test específico:     uv run python app/tests/test_runner.py --file test_schemas.py"
    )
    print(
        "• Solo performance:    uv run python app/tests/test_runner.py --performance"
    )
    print("• Ver estructura:      uv run python app/tests/test_runner.py --structure")


def main():
    """Función principal del test runner"""

    if len(sys.argv) == 1:
        # Sin argumentos, ejecutar todos los tests
        success = run_all_tests()
        sys.exit(0 if success else 1)

    arg = sys.argv[1]

    if arg == "--coverage":
        success = run_tests_with_coverage()
        sys.exit(0 if success else 1)

    elif arg == "--file" and len(sys.argv) > 2:
        test_file = sys.argv[2]
        success = run_specific_test_file(test_file)
        sys.exit(0 if success else 1)

    elif arg == "--performance":
        success = run_performance_tests()
        sys.exit(0 if success else 1)

    elif arg == "--check-deps":
        success = check_test_dependencies()
        sys.exit(0 if success else 1)

    elif arg == "--structure":
        show_test_structure()
        sys.exit(0)

    else:
        print("❌ Argumento no reconocido:", arg)
        print()
        show_test_structure()
        sys.exit(1)


if __name__ == "__main__":
    main()
