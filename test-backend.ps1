$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    phone = "13800000041"
    name = "CommitteeAdmin A"
    role = "COMMITTEE_ADMIN"
} | ConvertTo-Json

Write-Host "Testing backend login API..."
Write-Host "URL: http://localhost:6031/api/auth/login"
Write-Host "Body: $body"
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "http://localhost:6031/api/auth/login" -Method POST -Headers $headers -Body $body -TimeoutSec 5
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Response:"
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error occurred:"
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    }
}
