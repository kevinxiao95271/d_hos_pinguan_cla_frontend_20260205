# Test /api/admin/reviewers endpoint
$baseUrl = "http://localhost:6031"
$loginUrl = "$baseUrl/api/auth/login"
$reviewersUrl = "$baseUrl/api/admin/reviewers"

Write-Host "=== Testing /api/admin/reviewers API ===" -ForegroundColor Cyan

# Step 1: Login
Write-Host "[1/2] Logging in as committee admin..." -ForegroundColor Yellow
$loginBody = @{
    phone = "13800000041"
    name = "CommitteeAdmin A"
    role = "COMMITTEE_ADMIN"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri $loginUrl -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.data.token
    Write-Host "Login successful" -ForegroundColor Green
} catch {
    Write-Host "Login failed: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Get reviewers
Write-Host "[2/2] Fetching reviewers list..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    $uri = "$reviewersUrl" + "?competitionId=21&page=0&size=5"
    Write-Host "Calling: $uri"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers

    Write-Host "API call successful" -ForegroundColor Green

    Write-Host "Full API response:"
    $response | ConvertTo-Json -Depth 3

    if ($response.data.content) {
        $reviewers = $response.data.content
    } elseif ($response.data -is [Array]) {
        $reviewers = $response.data
    } else {
        $reviewers = @($response.data)
    }

    Write-Host "Total reviewers: $($reviewers.Count)" -ForegroundColor White

    if ($reviewers.Count -gt 0) {
        Write-Host "First reviewer:" -ForegroundColor Cyan
        $first = $reviewers[0]

        Write-Host "  ID: $($first.id)"
        Write-Host "  Name: $($first.name)"
        Write-Host "  Institution: $($first.institutionName)"

        if ($null -eq $first.institutionLevel) {
            Write-Host "  Level: NULL (MISSING)" -ForegroundColor Red
        } elseif ($first.institutionLevel -eq "") {
            Write-Host "  Level: EMPTY (MISSING)" -ForegroundColor Red
        } else {
            Write-Host "  Level: $($first.institutionLevel)" -ForegroundColor Green
        }

        Write-Host "Full response for first reviewer:"
        $first | ConvertTo-Json -Depth 2

        # Check all
        Write-Host "Checking all reviewers..."
        $withLevel = 0
        $withoutLevel = 0

        foreach ($r in $reviewers) {
            if ($null -ne $r.institutionLevel -and $r.institutionLevel -ne "") {
                $withLevel++
                Write-Host "  OK: $($r.name) - $($r.institutionLevel)" -ForegroundColor Green
            } else {
                $withoutLevel++
                Write-Host "  MISSING: $($r.name)" -ForegroundColor Red
            }
        }

        Write-Host "Summary: With level=$withLevel, Without level=$withoutLevel"

        if ($withoutLevel -gt 0) {
            Write-Host "ISSUE: Some reviewers missing institutionLevel!" -ForegroundColor Red
        } else {
            Write-Host "All reviewers have institutionLevel!" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "Failed to fetch reviewers: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Test complete" -ForegroundColor Cyan
