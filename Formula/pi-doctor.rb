class PiDoctor < Formula
  desc "Human-first Raspberry Pi diagnostics"
  homepage "https://github.com/Halfblood-Prince/pi-doctor"
  version "1.0.0"
  license "Apache-2.0"

  depends_on :linux

  on_linux do
    if Hardware::CPU.arm? && Hardware::CPU.is_64_bit?
      url "https://github.com/Halfblood-Prince/pi-doctor/releases/download/v1.0.0/pi-doctor-v1.0.0-aarch64-unknown-linux-gnu.tar.gz"
      sha256 "6602ae0764d69901e4a41a37224f68aef1675c16244a6c44a68bc405db805c70"
    elsif Hardware::CPU.arm?
      url "https://github.com/Halfblood-Prince/pi-doctor/releases/download/v1.0.0/pi-doctor-v1.0.0-armv7-unknown-linux-gnueabihf.tar.gz"
      sha256 "adea327f83cb6d071f09aff5bd5857a6496749f4f42b8df164a6f8db75d449bf"
    elsif Hardware::CPU.intel? && Hardware::CPU.is_64_bit?
      url "https://github.com/Halfblood-Prince/pi-doctor/releases/download/v1.0.0/pi-doctor-v1.0.0-x86_64-unknown-linux-gnu.tar.gz"
      sha256 "a05de2777a967f158e0b866e98dc3fecfebd16dd6f2ef5b196f6ff6167d2832e"
    end
  end

  def install
    bin.install "pi-doctor"
    bash_completion.install "completions/pi-doctor.bash" => "pi-doctor"
    zsh_completion.install "completions/_pi-doctor"
    fish_completion.install "completions/pi-doctor.fish"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/pi-doctor --version")
    system "#{bin}/pi-doctor", "support-bundle", "--dry-run"
  end
end
