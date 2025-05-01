resource "kubernetes_namespace" "honeypot" {
  metadata {
    name = "honeypot"
  }
}

resource "kubernetes_deployment" "cowrie" {
  metadata {
    name      = "cowrie"
    namespace = kubernetes_namespace.honeypot.metadata[0].name
    labels = {
      app = "cowrie"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "cowrie"
      }
    }

    template {
      metadata {
        labels = {
          app = "cowrie"
        }
      }

      spec {
        container {
          name  = "cowrie"
          image = "cowrie/cowrie:latest"
          ports {
            container_port = 2222
          }
          security_context {
            run_as_user  = 0
            run_as_group = 0
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "cowrie" {
  metadata {
    name      = "cowrie-service"
    namespace = kubernetes_namespace.honeypot.metadata[0].name
  }

  spec {
    selector = {
      app = "cowrie"
    }

    type = "NodePort"

    port {
      name        = "ssh"
      port        = 2222
      target_port = 2222
      node_port   = 32222 # Custom external port on node
    }
  }
}
