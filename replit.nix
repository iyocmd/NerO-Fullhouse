{pkgs}: {
  deps = [
    pkgs.run
    pkgs.libopus
    pkgs.ffmpeg
    pkgs.libsodium
    pkgs.ffmpeg-full
    pkgs.postgresql
    pkgs.openssl
  ];
}
