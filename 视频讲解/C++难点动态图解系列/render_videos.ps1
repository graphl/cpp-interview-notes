param(
    [string]$ProjectDir = $PSScriptRoot
)

$ErrorActionPreference = 'Stop'

function Find-Tool([string]$Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidate = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Gyan.FFmpeg*" `
        -Recurse -Filter "$Name.exe" -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName
    if (-not $candidate) {
        throw "$Name.exe not found"
    }
    return $candidate
}

$ffmpeg = Find-Tool 'ffmpeg'
$ffprobe = Find-Tool 'ffprobe'
$origin = Join-Path $ProjectDir 'origin_image'
$audioDir = Join-Path $ProjectDir 'audio'
$clipDir = Join-Path $ProjectDir 'clips'
$outputDir = Join-Path $ProjectDir 'mp4'
$narrationPath = Join-Path $ProjectDir 'narration.json'

foreach ($directory in @($audioDir, $clipDir, $outputDir)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}

$narrations = Get-Content -Raw -Encoding UTF8 $narrationPath | ConvertFrom-Json
if ($narrations.Count -ne 38) {
    throw "Expected 38 narration entries, got $($narrations.Count)"
}

for ($slide = 1; $slide -le 38; $slide++) {
    $imagePath = Join-Path $origin ('slide_{0:D2}.png' -f $slide)
    if (-not (Test-Path -LiteralPath $imagePath)) {
        throw "Missing slide image: $imagePath"
    }
}

Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.SelectVoice('Microsoft Huihui Desktop')
$speaker.Rate = 0
$speaker.Volume = 100

foreach ($item in $narrations) {
    $slide = [int]$item.slide
    $audioPath = Join-Path $audioDir ('slide_{0:D2}.wav' -f $slide)
    $speaker.SetOutputToWaveFile($audioPath)
    $speaker.Speak([string]$item.text)
    $speaker.SetOutputToNull()
}
$speaker.Dispose()

foreach ($item in $narrations) {
    $slide = [int]$item.slide
    $imagePath = Join-Path $origin ('slide_{0:D2}.png' -f $slide)
    $audioPath = Join-Path $audioDir ('slide_{0:D2}.wav' -f $slide)
    $clipPath = Join-Path $clipDir ('slide_{0:D2}.mp4' -f $slide)

    $durationText = & $ffprobe -v error -show_entries format=duration `
        -of default=noprint_wrappers=1:nokey=1 $audioPath
    $duration = [double]::Parse($durationText.Trim(), [Globalization.CultureInfo]::InvariantCulture) + 0.7
    $fadeOut = [Math]::Max(0.1, $duration - 0.35)
    $durationArg = $duration.ToString('0.###', [Globalization.CultureInfo]::InvariantCulture)
    $fadeOutArg = $fadeOut.ToString('0.###', [Globalization.CultureInfo]::InvariantCulture)

    $videoFilter = "scale=1920:1080:force_original_aspect_ratio=decrease," +
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0xFCFBF7," +
        "fade=t=in:st=0:d=0.25,fade=t=out:st=$fadeOutArg:d=0.35,format=yuv420p"

    & $ffmpeg -y -loglevel error -loop 1 -framerate 30 -i $imagePath -i $audioPath `
        -vf $videoFilter -af 'adelay=200|200,apad=pad_dur=0.5' `
        -t $durationArg -c:v libx264 -preset medium -crf 18 `
        -c:a aac -b:a 160k -movflags +faststart $clipPath
    if ($LASTEXITCODE -ne 0) {
        throw "ffmpeg failed for slide $slide"
    }
}

$videos = @(
    @{ Name = '01_从malloc到vector.mp4'; Start = 1; End = 7 },
    @{ Name = '02_一次虚函数调用.mp4'; Start = 8; End = 15 },
    @{ Name = '03_条件变量与内存序.mp4'; Start = 16; End = 23 },
    @{ Name = '04_ELF与PLT_GOT.mp4'; Start = 24; End = 30 },
    @{ Name = '05_epoll_Reactor数据流.mp4'; Start = 31; End = 38 }
)

foreach ($video in $videos) {
    $listPath = Join-Path $clipDir ($video.Name + '.concat.txt')
    $lines = for ($slide = $video.Start; $slide -le $video.End; $slide++) {
        $clipPath = (Join-Path $clipDir ('slide_{0:D2}.mp4' -f $slide)).Replace("'", "'\''")
        "file '$clipPath'"
    }
    [IO.File]::WriteAllLines($listPath, $lines, [Text.UTF8Encoding]::new($false))

    $outputPath = Join-Path $outputDir $video.Name
    & $ffmpeg -y -loglevel error -f concat -safe 0 -i $listPath `
        -c copy -movflags +faststart $outputPath
    if ($LASTEXITCODE -ne 0) {
        throw "concat failed for $($video.Name)"
    }
}

$report = foreach ($video in $videos) {
    $path = Join-Path $outputDir $video.Name
    $duration = & $ffprobe -v error -show_entries format=duration `
        -of default=noprint_wrappers=1:nokey=1 $path
    [pscustomobject]@{
        File = $path
        DurationSeconds = [Math]::Round([double]::Parse($duration.Trim(), [Globalization.CultureInfo]::InvariantCulture), 2)
        SizeMB = [Math]::Round((Get-Item -LiteralPath $path).Length / 1MB, 2)
    }
}

$report | Format-Table -AutoSize
