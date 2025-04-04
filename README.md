# Vaultify

FortiCrypt, dosyalarınızı güvenli bir şekilde şifrelemenize ve klasörlerinizi yönetmenize olanak tanıyan yüksek güvenlikli bir uygulamadır. Verilerinizi korumak için güçlü şifreleme kullanır ve yalnızca yetkili kullanıcılar erişebilir.

## Özellikler
- **Güvenli Dosya Şifreleme**: AES-256 ile dosyalarınızı koruyun.
- **Klasör Yönetimi**: Klasör oluşturun, silin ve yönetin.
- **Şifre Koruması**: Klasörlerinize ek parola ekleyin.
- **Kullanıcı Dostu Arayüz**: Kolay ve sezgisel kullanım.

## Kurulum
FortiCrypt’i bilgisayarınıza indirmek için aşağıdaki linki kullanın:

[**Vaultify İndir (Windows)**](https://github.com/KULLANICI_ADIN/forticrypt/releases/download/v1.0.0/FortiCrypt.exe)

### Kurulum Adımları
1. Yukarıdaki linke tıklayın ve `FortiCrypt.exe`’yi indirin.
2. İndirilen dosyaya çift tıklayın ve uygulamayı başlatın.
3. Giriş ekranında kullanıcı adı ve şifreyle oturum açın.

### Dosya Bütünlüğü Doğrulama
İndirdiğiniz dosyanın orijinal olduğunu doğrulamak için SHA-256 hash’ini kontrol edin:
- **SHA-256**: `[Adım 1’de hesapladığın hash,1a6315625e04be0f46ce7f9745d5e77190a2e4678b6f694463361ea1897244df]`
- Windows’ta hash’i kontrol etmek için:
  ```bash
  certutil -hashfile FortiCrypt.exe SHA256
