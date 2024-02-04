"""
GPT-in-a-Box Streamlit App
This module defines a Streamlit app for interacting with different Large Language models.
"""

import json
import yaml
import requests
import subprocess


class GetDeployment(object):
    def __init__(self, args):
        self.service_hostname = ""
        self.ingress_host = ""
        self.ingress_port = ""
        self.args = args

    def get_deployment_name(self):
        get_svc_hostname_cmd=f'kubectl get inferenceservice {self.args["deployment_name"]} ' + \
            '-o jsonpath=\'{.status.url}\' | cut -d "/" -f 3'

        svc = subprocess.run(
                             get_svc_hostname_cmd, 
                             shell=True, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             text=True
                            )

        get_ingress_host_cmd="kubectl get po -l istio=ingressgateway -n istio-system -o jsonpath='{.items[0].status.hostIP}'"
        host = subprocess.run(get_ingress_host_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        get_port_cmd="kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name==\"http2\")].nodePort}'"
        port = subprocess.run(get_port_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if svc.stderr or host.stderr or port.stderr:
            st.error(f"Encountered 1 or more errors when running kubectl commands, please check that your KUBECONFIG is valid and your cluster is running \n" \
            f"{svc.stderr}\n" \
            f"{host.stderr}\n" \
            f"{port.stderr}\n")
            st.stop()

        self.service_hostname = svc.stdout.strip()
        self.ingress_host = host.stdout.strip()
        self.ingress_port = port.stdout.strip()


