$env:PYTHONPATH = "d:\knacklab\api"
$process = Start-Process -FilePath "d:\knacklab\api\.venv\Scripts\uvicorn.exe" -ArgumentList "app.main:app", "--port", "8000", "--host", "127.0.0.1" -PassThru

Start-Sleep -Seconds 3

$evidenceFile = "d:\knacklab\progress\evidence\module-03\api-evidence.txt"
"" > $evidenceFile

function Log-Output($title, $content) {
    Add-Content -Path $evidenceFile -Value "======================================"
    Add-Content -Path $evidenceFile -Value $title
    Add-Content -Path $evidenceFile -Value "======================================"
    Add-Content -Path $evidenceFile -Value $content
    Add-Content -Path $evidenceFile -Value ""
}

try {
    # 1. Health check
    $health = curl.exe -s -i "http://localhost:8000/health"
    Log-Output "1. HEALTH CHECK: GET /health" ($health -join "`n")

    # 2. Valid link creation
    $createJson = '{"long_url":"https://example.com"}'
    $createResp = curl.exe -s -i -X POST "http://localhost:8000/links" -H "Content-Type: application/json" -d $createJson
    Log-Output "2. CREATE LINK: POST /links with https://example.com" ($createResp -join "`n")

    # Extract code from response
    $bodyLine = ($createResp | Where-Object { $_ -match '"code":' })[0]
    $codeMatch = [regex]::Match($bodyLine, '"code":"([^"]+)"')
    $code = $codeMatch.Groups[1].Value

    if ($code) {
        # 3. Valid redirect
        $redirectResp = curl.exe -s -i "http://localhost:8000/r/$code"
        Log-Output "3. REDIRECT: GET /r/$code" ($redirectResp -join "`n")

        # 4. Get link by id
        $idMatch = [regex]::Match($bodyLine, '"id":([0-9]+)')
        $id = $idMatch.Groups[1].Value
        $getResp = curl.exe -s -i "http://localhost:8000/links/$id"
        Log-Output "4. GET LINK BY ID: GET /links/$id" ($getResp -join "`n")
    }

    # 5. Non-existent code (expect 404)
    $notFoundResp = curl.exe -s -i "http://localhost:8000/r/nonexistentcode999"
    Log-Output "5. NOT FOUND REDIRECT: GET /r/nonexistentcode999 (Expect 404)" ($notFoundResp -join "`n")

    # 6. Abuse tests (expect 400 Bad Request)
    $abuseCases = @(
        "javascript:alert(1)",
        "JaVaScRiPt:alert(1)",
        " javascript:alert(1) ",
        "data:text/html,<svg/onload=alert(1)>",
        "//evil.example.com",
        "http:%2f%2fevil.example.com",
        "http%3A%2F%2Fevil.example.com",
        "http:\\evil.example.com",
        "https://good.com@evil.example.com"
    )

    foreach ($case in $abuseCases) {
        $escaped = $case.Replace('\', '\\').Replace('"', '\"')
        $payload = "{`"long_url`":`"$escaped`"}"
        $abuseResp = curl.exe -s -i -X POST "http://localhost:8000/links" -H "Content-Type: application/json" -d $payload
        $statusLine = ($abuseResp | Select-Object -First 1)
        Log-Output "ABUSE CHECK ($statusLine): $case" ($abuseResp -join "`n")
    }
}
finally {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
}
