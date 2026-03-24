#!/usr/bin/env ruby
require 'net/http'
require 'uri'
require 'json'

server_ip = "202:184a:fd9:c392:c10b:4621:62be:9003"
server_port = 8080
api_token = "my_secret_token"

base_url = "http://[#{server_ip}]:#{server_port}"
upload_uri = URI("#{base_url}/upload")

puts "[*] поиск файлов .md в текущей директории..."

md_files = Dir.glob("*.md")

if md_files.empty?
  puts "[!] файлы .md не найдены"
  exit
end

puts "[*] найдено файлов: #{md_files.count}"
puts "[*] начало отправки на #{base_url}..."
puts ""

http = Net::HTTP.new(server_ip, server_port)

http.open_timeout = 10
http.read_timeout = 30

headers = {
  'X-Auth-Token' => api_token,
  'User-Agent' => 'YggdrasilRubyClient/1.0'
}

md_files.each do |file_path|
  filename = File.basename(file_path)
  
  begin
    file_content = File.read(file_path)
    boundary = "----RubyBoundary#{Time.now.to_i}#{rand(1000)}"
    
    body = ""
    body += "--#{boundary}\r\n"
    body += "Content-Disposition: form-data; name=\"file\"; filename=\"#{filename}\"\r\n"
    body += "Content-Type: text/markdown\r\n"
    body += "\r\n"
    body += "#{file_content}\r\n"
    body += "--#{boundary}--\r\n"
    
    headers['Content-Type'] = "multipart/form-data; boundary=#{boundary}"
    
    request = Net::HTTP::Post.new(upload_uri.path, headers)
    request.body = body
    
    response = http.request(request)
    
    if response.code == "201"
      data = JSON.parse(response.body)
      puts "[+] файл: #{filename}"
      puts "    ссылка: #{data['link']}"
      puts "-" * 40
    else
      puts "[-] ошибка отправки #{filename}: #{response.code}"
      puts "    ответ: #{response.body}"
    end
    
  rescue Errno::ECONNREFUSED, Errno::ENETUNREACH => e
    puts "[-] ошибка соединения: требуется проверка ipv6 адреса и сети yggdrasil"
    puts "    детали: #{e.message}"
    exit
  rescue SocketError => e
    puts "[-] ошибка разрешения адреса: проверьте формат ipv6"
    puts "    детали: #{e.message}"
    exit
  rescue => e
    puts "[-] непредвиденная ошибка с файлом #{filename}"
    puts "    детали: #{e.message}"
  end
end

puts "[*] готово"