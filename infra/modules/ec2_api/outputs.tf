output "public_ip" {
  description = "Instance's public IP - changes every demo-up cycle since there's no Elastic IP (DNS is repointed each time instead)."
  value       = aws_instance.this.public_ip
}

output "instance_id" {
  value = aws_instance.this.id
}
