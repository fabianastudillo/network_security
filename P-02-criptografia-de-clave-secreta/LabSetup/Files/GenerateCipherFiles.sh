#!/bin/bash

# Función para extraer texto de la web sin copyright
# Parámetro: $1 - año (formato: Mar-2024, Sep-2024, etc.)
# Retorna: nombre del archivo generado


# Función para mostrar ayuda
mostrar_ayuda() {
    echo "Uso: $0 [opciones]"
    echo "Opciones:"
    echo "  -c          Crear archivos de texto cifrado"
    echo "  -n NUM      Número de grupos (por defecto: 5)"
    echo "  -s SEM      Semestre (ej: Mar, Sep)"
    echo "  -y AÑO      Año (ej: 2025)"
    echo "  -r          Eliminar archivos de texto cifrado"
    echo "  -e          Eliminar archivo de texto claro"
    echo "  -h          Mostrar esta ayuda"
    exit 0
}

# Mostrar ayuda si no hay parámetros
if [ "$#" -eq 0 ]; then
    echo "No se proporcionaron parámetros."
    mostrar_ayuda
fi

# Valores por defecto
crear_cifrado=false
number_of_groups=5
eliminar_cifrados=false
eliminar_claro=false
semester=""
year=""

extraer_texto_web() {
    local year="$1"
    local output_file="textoclaro-${year}.txt"
    
    # URL de Project Gutenberg (dominio público, sin copyright)
    local url="https://www.gutenberg.org/files/1342/1342-0.txt"
    
    # Descargar y procesar el texto
    curl -s "$url" | \
        head -n 1000 | \
        tail -n 100 | \
        tr '[:upper:]' '[:lower:]' | \
        perl -pe '
            s/(\d+)/
                my $num = $1;
                my %digits = (
                    "0" => "cero", "1" => "uno", "2" => "dos", "3" => "tres", "4" => "cuatro",
                    "5" => "cinco", "6" => "seis", "7" => "siete", "8" => "ocho", "9" => "nueve"
                );
                $num =~ s#(\d)#$digits{$1}#ge;
                $num;
            /ge
        ' | \
        tr -cd '[a-z][\n][:space:]' | \
        head -c 10000 > "$output_file"
    echo "$output_file"
}

while getopts "cn:s:y:reh" opt; do
    case $opt in
        c) crear_cifrado=true ;;
        n) number_of_groups="$OPTARG" ;;
        s) semester="$OPTARG" ;;
        y) year="$OPTARG" ;;
        r) eliminar_cifrados=true ;;
        e) eliminar_claro=true ;;
        h) mostrar_ayuda ;;
        *) mostrar_ayuda ;;
    esac
done

# Eliminar archivo de texto claro
if [ "$eliminar_claro" = true ]; then
    rm -f textoclaro-*.txt claves-*.txt
    echo "Archivo(s) de texto claro eliminado(s)."
fi

# Eliminar archivos cifrados
if [ "$eliminar_cifrados" = true ]; then
    rm -f textoCifradoGrupo*.bin
    echo "Archivos de texto cifrado eliminados."
fi

# Crear archivos cifrados
if [ "$crear_cifrado" = true ]; then
    # Obtener semestre y año actual
    current_month=$(date +%m)
    current_year=$(date +%Y)
    if [ "$current_month" -ge 3 ] && [ "$current_month" -lt 9 ]; then
        semester="Mar"
    else
        semester="Sep"
    fi
    year="$current_year"
    period="${semester}-${year}"
    texto_archivo=$(extraer_texto_web "$period")

    echo "Archivos cifrados creados para $number_of_groups grupos."
    for i in $(seq 1 $number_of_groups); do    
        clave=$(echo {a..z} | sed 's/ /\n/g' | shuf | tr '\n' ' ' | sed 's/ //g')
        tr 'a-z' "$clave" < "$texto_archivo" > "textoCifradoGrupo${i}.bin"
        echo "$clave" >> "claves-${year}.txt"
    done
fi