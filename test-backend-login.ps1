$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    phone = "13800000041"
    name = "CommitteeAdmin A"
    role = "COMMITTEE_ADMIN"
} | ConvertTo-Json

Write-Host "Testing backend login API with 30 second timeout..."
Write-Host "URL: http://localhost:6031/api/auth/login"
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "http://localhost:6031/api/auth/login" -Method POST -Headers $headers -Body $body -TimeoutSec 30
    Write-Host "✓ Success! Status: $($response.StatusCode)"
    Write-Host ""
    Write-Host "Response:"
    $jsonResponse = $response.Content | ConvertFrom-Json
    $jsonResponse | ConvertTo-Json -Depth 10

    if ($jsonResponse.success -and $jsonResponse.data.token) {
        Write-Host ""
        Write-Host "✓ Login successful!"
        Write-Host "Token: $($jsonResponse.data.token.Substring(0, 50))..."
    }
} catch {
    Write-Host "✗ Error occurred:"
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody"
    }
}
