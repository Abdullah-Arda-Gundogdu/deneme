
from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
from pydantic import BaseModel
from langchain_ibm import WatsonxEmbeddings, WatsonxLLM
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain.tools.render import render_text_description_and_args
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from langgraph.graph import StateGraph
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ibm import WatsonxLLM  # Placeholder; use IBM LLM
from langchain.schema import Document
from langchain_community.document_loaders import PyMuPDFLoader
import uuid
import os
from langchain.document_loaders import Docx2txtLoader
import re
import pandas as pd
import time  # For measuring execution time
import xml.etree.ElementTree as ET
import requests
from ibm_watsonx_ai.helpers.connections import DataConnection, AssetLocation
from ibm_watsonx_ai import APIClient, Credentials
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import base64
import zipfile
import shutil
from sqlalchemy import create_engine, text
import json
from datetime import datetime
from chromadb.config import Settings

from elasticsearch8 import Elasticsearch
from datetime import datetime
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

from datetime import datetime
import json
import base64
import zipfile
import requests
import time
import cx_Oracle
from utils.pipelines.main import get_last_user_message, get_last_assistant_message
agent = None

class BasvuruDetay:
    def __init__(self,basvuruSahibiHesapSahibi,basvuruSahibiIBAN,uyusmazlikKararTarihi,uyusmazlikTutari,hakemAd,hakemSoyad):
        self.basvuruSahibiHesapSahibi = basvuruSahibiHesapSahibi
        self.basvuruSahibiIBAN = basvuruSahibiIBAN
        self.uyusmazlikKararTarihi = uyusmazlikKararTarihi
        self.uyusmazlikTutari = uyusmazlikTutari
        self.hakemAd = hakemAd
        self.hakemSoyad = hakemSoyad

    def __repr__(self):
        return f"BasvuruDetay({vars(self)})"

class EvrakNo:
    def __init__(self, evrak_no):
        self.evrak_no = evrak_no

    def __repr__(self):
        return f"EvrakNo(evrak_no='{self.evrak_no}')"

class EvrakDetay:
    def __init__(self, dokuman):
        self.dokuman = dokuman

    def __repr__(self):
        return f"EvrakDetay(dokuman='<binary data>')"
        
class BasvuruNo:
    def __init__(self, basvuru_no, sigorta_sirket_kodu, basvuru_durum_aciklama):
        self.basvuru_no = basvuru_no
        self.sigorta_sirket_kodu = sigorta_sirket_kodu
        self.basvuru_durum_aciklama = basvuru_durum_aciklama

    def __repr__(self):
        return f"BasvuruNo(basvuru_no='{self.basvuru_no}', sigorta_sirket_kodu='{self.sigorta_sirket_kodu}', basvuru_durum_aciklama='{self.basvuru_durum_aciklama}')"




class Pipeline:

    class Valves(BaseModel):
        pass
    
    def __init__(self):
        self.name = "ToolUpdate"
        pass
    
    
    ###################################
    #BURASI BASLANGIC




    class DataLoader:
        def __init__(self):
            
            self.SOAP_URL = "https://ws.sbm.org.tr:443/SBM-TahkimWS/TahkimBasvuruSorguService"
            self.HEADERS = {
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": ""
            }
            self.ns = {
                "S": "http://schemas.xmlsoap.org/soap/envelope/",
                "env": "http://schemas.xmlsoap.org/soap/envelope/",
                "ns0": "http://basvurusorgu.sbm-tahkim.org.tr",
                "islem": "http://sbm.org.tr/islem",
                "work": "http://oracle.com/weblogic/soap/workarea/",
            }

        def basvuru_no_sorgu(self,olusturma_tarihi):
            soap_body = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                            xmlns:bas="http://basvurusorgu.sbm-tahkim.org.tr">
                <soapenv:Header>
                    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                        <wsse:UsernameToken>
                            <wsse:Username>gunes</wsse:Username>
                            <wsse:KurumKod>026</wsse:KurumKod>
                            <wsse:IstemciKimlikTipi>2</wsse:IstemciKimlikTipi>
                            <wsse:IstemciKimlikNo>4340056984</wsse:IstemciKimlikNo>
                        </wsse:UsernameToken>
                    </wsse:Security>
                </soapenv:Header>
                <soapenv:Body>
                    <bas:basvuruNoSorgu>
                        <arg0>
                            <olusturmaTarihi>{olusturma_tarihi}</olusturmaTarihi>
                            <sigortaSirketKodu>026</sigortaSirketKodu>
                        </arg0>
                    </bas:basvuruNoSorgu>
                </soapenv:Body>
            </soapenv:Envelope>
            """
            response = requests.post(self.SOAP_URL, data=soap_body, headers=self.HEADERS)
            return response.text

        def basvuru_detay_sorgu(self,basvuru_no):
            soap_body = f"""
            <soapenv:Envelope 
                xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                <soapenv:Header>
                    <Security 
                        xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                        <UsernameToken>
                            <Username>gunes</Username>
                            <KurumKod>026</KurumKod>
                            <IstemciKimlikTipi>2</IstemciKimlikTipi>
                            <IstemciKimlikNo>4340056984</IstemciKimlikNo>
                        </UsernameToken>
                    </Security>
                </soapenv:Header>
                <soapenv:Body>
                    <ns3:basvuruDetaySorgu
                        xmlns:ns3="http://basvurusorgu.sbm-tahkim.org.tr">
                        <arg0>
                            <basvuruNo>{basvuru_no}</basvuruNo>
                            <sigortaSirketKodu>026</sigortaSirketKodu>
                        </arg0>
                    </ns3:basvuruDetaySorgu>
                </soapenv:Body>
            </soapenv:Envelope>
            """
            response = requests.post(self.SOAP_URL, data=soap_body, headers=self.HEADERS)
            return response.text

        def basvuru_evrak_no_sorgu(self,basvuru_no, evrak_turu):
            soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Header>
            <Security xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                <UsernameToken>
                    <Username>gunes</Username>
                    <KurumKod>026</KurumKod>
                    <IstemciKimlikTipi>2</IstemciKimlikTipi>
                    <IstemciKimlikNo>4340056984</IstemciKimlikNo>
                </UsernameToken>
            </Security>
        </soapenv:Header>
        <soapenv:Body>
            <ns3:basvuruEvrakNoSorgu xmlns:ns3="http://basvurusorgu.sbm-tahkim.org.tr">
                <arg0>
                    <basvuruNo>{basvuru_no}</basvuruNo>
                    <evrakType>{evrak_turu}</evrakType>
                    <sigortaSirketKodu>026</sigortaSirketKodu>
                </arg0>
            </ns3:basvuruEvrakNoSorgu>
        </soapenv:Body>
        </soapenv:Envelope>"""
            response = requests.post(self.SOAP_URL, data=soap_body, headers=self.HEADERS)
            return response.text

        def basvuru_evrak_sorgu(self,evrak_no):
            soap_body = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                            xmlns:bas="http://basvurusorgu.sbm-tahkim.org.tr">
                <soapenv:Header>
                    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                        <wsse:UsernameToken>
                            <wsse:Username>gunes</wsse:Username>
                            <wsse:KurumKod>026</wsse:KurumKod>
                            <wsse:IstemciKimlikTipi>2</wsse:IstemciKimlikTipi>
                            <wsse:IstemciKimlikNo>4340056984</wsse:IstemciKimlikNo>
                        </wsse:UsernameToken>
                    </wsse:Security>
                </soapenv:Header>
                <soapenv:Body>
                    <bas:basvuruEvrakSorgu>
                        <arg0>
                            <evrakNo>{evrak_no}</evrakNo>
                            <sigortaSirketKodu>026</sigortaSirketKodu>
                        </arg0>
                    </bas:basvuruEvrakSorgu>
                </soapenv:Body>
            </soapenv:Envelope>
            """


            
            response = requests.post(self.SOAP_URL, data=soap_body, headers=self.HEADERS)
            return response.text

        def parse_basvuru_no_sorgu_response(self,response_xml):
            root = ET.fromstring(response_xml)
            basvuru_list = []
            for basvuru in root.findall(".//basvuru"):
                basvuru_no = basvuru.find("basvuruNo").text
                sigorta_sirket_kodu = basvuru.find("sigortaSirketKodu").text
                basvuru_durum_aciklama = basvuru.find("basvuruDurumAciklama").text
                basvuru_list.append(BasvuruNo(basvuru_no, sigorta_sirket_kodu, basvuru_durum_aciklama))
            return basvuru_list

        def parse_basvuru_evrak_no_sorgu_response(self,response_xml):
            try:
                if response_xml is not None:
                    root = ET.fromstring(response_xml)
                    evrak_no_list = []
                    for evrak_no in root.findall(".//evrakNo"):
                        evrak_no_list.append(EvrakNo(evrak_no.text))
                    return evrak_no_list
                else:
                    pass
            except Exception as e:
                print(f"Bir hata olustu: {e}") 


        def parse_basvuru_evrak_sorgu_response(self,response_xml):
            root = ET.fromstring(response_xml)
            dokuman = root.find(".//dokuman").text
            return EvrakDetay(dokuman)


        def parse_xml_to_basvuru_detay(self,response_xml) -> BasvuruDetay:
            root = ET.fromstring(response_xml)
            data = {}
            
            fields = [
                ("basvuruSahibiHesapSahibi", ".//basvuruSahibiHesapSahibi"),
                ("basvuruSahibiIBAN", ".//basvuruSahibiIBAN"),
                ("uyusmazlikKararTarihi", ".//uyusmazlikKararTarihi"),
                ("uyusmazlikTutari", ".//uyusmazlikTutari"),
                ("hakemAd", ".//hakemAd"),
                ("hakemSoyad", ".//hakemSoyad"),
            ]
            
            for field, path in fields:
                element = root.find(path, namespaces=self.ns)
                if element is not None:
                    data[field] = element.text
                else:

                    data[field] = None

            return BasvuruDetay(**data)



        def get_data_from_hs(self,hukuk_dosya_no):
            dsn_tns = cx_Oracle.makedsn("tsx9m-scan.trs.local", "1568", service_name="dwh")
            kullanici_adi = "WATSONXAI"
            sifre = "Wtest.u22"

            try:

                connection = cx_Oracle.connect(user=kullanici_adi, password=sifre, dsn=dsn_tns)


                cursor = connection.cursor()


                query = """
                    SELECT *
                    FROM ROTA_PRJ.IDWH_8879_ODEME
                    WHERE HUKUK_DOSYA_NO = :hukuk_dosya_no
                """


                cursor.execute(query, {"hukuk_dosya_no": hukuk_dosya_no})
                columns = [col[0] for col in cursor.description]  
                results = cursor.fetchall()


                data = []
                for row in results:

                    row_dict = dict(zip(columns, row))
                    
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")  
                            

                    dosya_esas_yil = int(row_dict["DOSYA_ESAS_YIL"])
                    dosya_esas_format = row_dict["DOSYA_ESAS_FORMAT"]
                    dosya_esas_sira = int(row_dict["DOSYA_ESAS_SIRA"])
                    combined_string = f"{dosya_esas_yil}{dosya_esas_format}{dosya_esas_sira}"


                    row_dict["SBMSORGU"] = combined_string
                    data.append(row_dict)


                return json.dumps(data, ensure_ascii=False, indent=4)

            except cx_Oracle.DatabaseError as e:
                return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)

            finally:

                if 'cursor' in locals():
                    cursor.close()
                if 'connection' in locals():
                    connection.close()

#--------------------------------------------------

        def get_evrak_id_eksper(self,hasar_dosya_no):
            kullanici_adi = "WATSONXAI"
            sifre = "Wtest.u22"
            try:
                engine = create_engine(f"oracle+cx_oracle://{kullanici_adi}:{sifre}@tsx9m-scan.trs.local:1568/?service_name=dwh")
                with engine.connect() as connection:
                    query = text("""
                        SELECT YENI_DYS_ID, ACIKLAMA
                        FROM ROTA_PRJ.IDWH_8879_EVRAK2
                        WHERE HASAR_DOSYA_NO = :hasar_dosya_no
                    """)
                    results = connection.execute(query, {"hasar_dosya_no": hasar_dosya_no}).fetchall()
                    for x in results:
                        if x[1] == "KAT{} EKSPERT{}Z RAPORU".format(chr(304),chr(304),chr(304)):
                            evrak_id = x[0]
                            
                    return evrak_id

            except Exception as e:
                    print(e)
                    return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)

        # Access token alma fonksiyonu
        def get_access_token_eksper(self):
            url = "https://apigw-test.turkiyesigorta.com.tr/auth/oauth/v2/token"
            data = {
                "grant_type": "password",
                "username": "WS_HUKUK",
                "password": "Aa123456",
                "scope": "token",
                "client_id": "54f0c455-4d80-421f-82ca-9194df24859d",
                "client_secret": "a0f2742f-31c7-436f-9802-b7015b8fd8e6"
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(url, data=data, headers=headers)
            return response.json().get('access_token')

        # Evrak indirme fonksiyonu
        def download_evrak_as_pdf_eksper(self,evrak_id, save_dir):
            token = self.get_access_token_eksper()
            if not token:
                print("Access token alinamadi.")
                return

            url = "https://pusulawsi.turkiyesigorta.com.tr/rest/HukukRestService/evrakIndir/"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            response = requests.post(url, json={"evrakID": evrak_id}, headers=headers, verify=False)

            if response.status_code != 200:
                print(f"Hata: {response.status_code}")
                return

            try:
                data = response.json()
            except ValueError:
                print("Gecersiz JSON.")
                return

            if data.get('status') == 'SUCCESS' and data.get('result'):
                byte_array = data['result']['dosya']
                file_name = data['result']['dosyaAdi'].replace('.jpg', '.pdf')
                pdf_bytes = bytes([(b + 256) if b < 0 else b for b in byte_array])

                os.makedirs(save_dir, exist_ok=True)
                path = os.path.join(save_dir, file_name)
                with open(path, "wb") as f:
                    f.write(pdf_bytes)
                print(f"{file_name} basariyla indirildi.")
                return file_name
            else:
                print("Evrak indirilemedi veya icerik bobos.")
                return "asd"



#---------------------------------------------------
        def extract_sbm_files(self,evrak_no):
            try:
                root = ET.fromstring(self.basvuru_evrak_sorgu(evrak_no))


                dokuman = root.find('.//dokuman')

                if dokuman is not None:

                    dokuman_content = dokuman.text.strip()

                    base64_data = dokuman_content
            

                    decoded_data = base64.b64decode(base64_data)
            

                    output_file = "output.zip"
                    with open(output_file, "wb") as file:
                        file.write(decoded_data)

                    print(f"Base64 verisi {output_file} adkiyla kaydedildi.")

                    extract_folder = "hs_rag"
                    with zipfile.ZipFile(output_file, "r") as zip_ref:
                        zip_ref.extractall(extract_folder)
                    
                    print(f"ZIP dosyas '{extract_folder}' klas cik.")
                else:
                    print("<dokuman> etiketi bulunamadk.")
            except Exception as e:
                print(f"Bir hata olustu: {e}")  
        def extract_sbm_files_last(self,hukuk_dosya_no):

            start_time = time.time()
            result = self.get_data_from_hs(hukuk_dosya_no)
            

            total_requests = 0
            successful_responses = 0
            data = json.loads(result)
            if isinstance(data, dict) and "error" in data:
                print(f"Hata: {data['error']}")
            else:
                if data:  
                    first_row = data[0] 
                    evrak_no_str = first_row.get("SBMSORGU")
                    if evrak_no_str:
                        print(f"ilk satir SBMSORGU: {evrak_no_str}")
                    else:
                        print("SBMSORGU bulunamadi.")
                else:
                    print("Sonuclar bso.")

                evrak_turleri = [
                    "BASVURU_DOKUMANI",
                    "BASVURU_SIRKET_CEVABI",
                    "BASVURU_IMZALI_HAKEM_KARARI",
                    "BILIRKISI_RAPOR"
                ]
            
                for evrak_turu in evrak_turleri:
                    total_requests += 1  
                    
                    evrak_no_list = self.parse_basvuru_evrak_no_sorgu_response(self.basvuru_evrak_no_sorgu(evrak_no_str, evrak_turu))
                   # print(self.parse_basvuru_evrak_no_sorgu_response(self.basvuru_evrak_no_sorgu(evrak_no_str, evrak_turu)))
                    if evrak_no_list is not None:
                        for evrak_no in evrak_no_list:
                            print(f"Evrak No: {evrak_no.evrak_no}")
                            self.extract_sbm_files(evrak_no.evrak_no)
                            successful_responses += 1  
            

            end_time = time.time()
            elapsed_time = end_time - start_time
            
            print("\nisslem Tamamlandi!")
            print(f"Toplam Gecen Sure: {elapsed_time:.2f} saniye")
            print(f"Toplam Yapilan Sorgu: {total_requests}")
            print(f"Basari Yanit Sayisi: {successful_responses}")


    ######################################

    class BaseRetrival():
        def __init__(self):
            os.environ["WATSONX_APIKEY"] = "ljjOHUaNoxjrok6d2zIGPQhmYG8VKfMOFHlT0hmy"
            self.embedding_model_id = "intfloat/multilingual-e5-large"#"sentence-transformers/all-minilm-l6-v2"
            self.model_id ="meta-llama/llama-3-3-70b-instruct"
            self.url= "https://cpd-ibm-cpd-instance.apps.ocpai.turkiyesigorta.com.tr/"
            self.api_key ="ljjOHUaNoxjrok6d2zIGPQhmYG8VKfMOFHlT0hmy"
            self.space_id = "3e3b6b9a-7812-4a30-9fcf-19de30f4f3de"
            self.project_id = "2ed5840f-2433-4d29-9fa9-3f2e0613a558"
            self.instance_id= "openshift"
            self.username  = "cpadmin"
            self.es = Elasticsearch("http://10.20.21.237:9200")

            self.password ="swYO11qODwlhffktd55R0qtbDPfjO7Xn"
            self.base_index = "base_index_test6"#"base_index_test5"
            self.create_index_if_not_exists()
            self.set_models()
            
        def set_models(self):
            credentials = {
                "url": self.url,
                "apikey": self.api_key
            }

            self.embeddings = WatsonxEmbeddings(
                model_id=self.embedding_model_id,
                url=credentials["url"],
                apikey=self.api_key,
                project_id=self.project_id,
                username=self.username,
                password=self.password,
                instance_id= self.instance_id
            )
        def create_index_if_not_exists(self):
            # Define custom mappings (optional, you can adjust them as needed)
            mappings_base = {
                    "properties": {
                        "page_content": {"type": "text"},
                        "id": {"type": "keyword"},
                        "file_name": {"type": "keyword"},
                        "page_num": {"type": "integer"},
                        "chunk_idx": {"type": "integer"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 1024,
                            "index": True,
                            "similarity" : "cosine"  # Adjust to your actual embedding dimension
                        }
                    }
            
            }

            # Check if the index exists
            if not self.es.indices.exists(index=self.base_index):
                # Create the index with the specified mappings
                self.es.indices.create(index=self.base_index, body={
                    "mappings": mappings_base
                })

                print(f"Index '{self.base_index}' created.")
            else:
                print(f"Index '{self.base_index}' already exists.")

        def store_retrieved_docs(self,chunks):
            try:
                for doc in chunks:
                    self.es.index(index=self.base_index, document={
                                "id": doc.metadata["id"],
                                "file_name": doc.metadata["file_name"],
                                "page_num": doc.metadata["page_num"],
                                "chunk_idx": doc.metadata["chunk_idx"],
                                "page_content" : doc.page_content,
                                "embedding" : doc.metadata["embedding"]

                    })
            except Exception as e:
                print("Here::::")
                print(e)


        def chunk_pdf(self,path):  
            loader = PyPDFLoader(path)  
            pages = loader.load()  
            splitter = RecursiveCharacterTextSplitter(chunk_size=1250, chunk_overlap=250)  
            chunks = []  
            for i, page in enumerate(pages):  
                texts = splitter.split_text(page.page_content)  
                for j, text in enumerate(texts):  
                    chunks.append(Document(  
                        page_content=text,  
                        metadata={  
                            "id" : str(uuid.uuid4()),
                            "file_name": path,  
                            "page_num" : i,
                            "chunk_idx": j,
                            "embedding" : self.embeddings.embed_query(text)

                            #new fields may added.
                        }  
                    ))  
            return chunks  


        def chunk_all_pdfs_from_list(self,pdf_list):
            all_chunks = []
            
            for pdf_file in pdf_list:
                print(pdf_file)
                chunks = self.chunk_pdf(pdf_file)
                all_chunks.extend(chunks)
            
            return all_chunks


        def run(self, base_pdfs):
            # Get document chunks from the list of PDFs
            all_chunks = self.chunk_all_pdfs_from_list(base_pdfs)

            self.store_retrieved_docs(all_chunks)


            """            faiss_index = FAISS.from_documents(
                documents=all_chunks,
                embedding=self.embeddings
            )"""




    #Retrieval for Hukuk Dosya No

    #Helper tool for base document retrival >
    class HukukRetrival():
        def __init__(self):
            self.embedding_model_id ="intfloat/multilingual-e5-large" #"sentence-transformers/all-minilm-l6-v2"
            self.model_id ="meta-llama/llama-3-3-70b-instruct"
            self.url= "https://cpd-ibm-cpd-instance.apps.ocpai.turkiyesigorta.com.tr/"
            self.api_key ="ljjOHUaNoxjrok6d2zIGPQhmYG8VKfMOFHlT0hmy"
            self.space_id = "3e3b6b9a-7812-4a30-9fcf-19de30f4f3de"
            self.project_id = "2ed5840f-2433-4d29-9fa9-3f2e0613a558"
            self.instance_id= "openshift"
            self.username  = "cpadmin"
            self.eksper_index = "eksper_index_test1"#"eksper_index"
            self.es = Elasticsearch("http://10.20.21.237:9200")
            self.password ="swYO11qODwlhffktd55R0qtbDPfjO7Xn"
            self.set_models()
            self.eksper_check_index()

        def eksper_check_index(self):
            print("eksper chunk creation")
            mappings_full_text = {
            "properties": {
                "hukuk_dosya_no": {
                    "type": "keyword"
                },
                "full_text": {
                    "type": "text",  # store large text content
                   # "index": False   # optional: disable indexing if not needed
                }
            }
            }
            try:
                if not self.es.indices.exists(index=self.eksper_index):
                    self.es.indices.create(index=self.eksper_index, body={
                        "mappings": mappings_full_text
                    })
                    print(f"Index '{self.eksper_index}' created. NENE")
                else:
                    print(f"Index '{self.eksper_index}' already exists.NENE")
            except Exception as e:
                print("NENENE")
                print(e)
        def eksper_load_data(self,text,hukuk_dosya_no):
            try:
                self.es.index(
                index=self.eksper_index,
                document={
                    "hukuk_dosya_no": hukuk_dosya_no,
                    "full_text": text  # a long string (the full content of a PDF)
                }
                )
            except:
                print("HATA ! eksper_load_data basarisiz")

        def eksper_already_exist(self,hukuk_dosya_no):
            try:
                response = self.es.search(index=self.eksper_index, body={
                    "query": {
                                "match": {
                            "hukuk_dosya_no": hukuk_dosya_no
                        }  # This matches all documents in the index
                    },
            "size": 1
                })

                return response["hits"]["total"]["value"] > 0

            except Exception as e:
                print(f"[ERROR] Failed to query Elasticsearch: {e}")
                return False
            
        def eksper_get_data(self,hukuk_dosya_no):
            response = self.es.search(
            index=self.eksper_index,
            query={
                "term": {
                    "hukuk_dosya_no": hukuk_dosya_no # Replace with the actual value
                }
                }
            )

            # Process and return the result
            if response["hits"]["hits"]:
                doc = response["hits"]["hits"][0]["_source"]
                full_text = doc["full_text"]

                return full_text
            else:
                print("No document found for given hukuk_dosya_no.")
                return None


        def set_models(self):
            credentials = {
                "url": self.url,
                "apikey": self.api_key
            }

            self.embeddings = WatsonxEmbeddings(
                model_id=self.embedding_model_id,
                url=credentials["url"],
                apikey=self.api_key,
                project_id=self.project_id,
                username=self.username,
                password=self.password,
                instance_id= self.instance_id
            )

        def get_chunk_of_file(self,path,doc_type):
            print("get_chunk_of_file")
            ext = os.path.splitext(path)[1].lower()
            if ext == ".pdf":
                loader = PyPDFLoader(path)
            elif ext == ".docx":
                loader = Docx2txtLoader(path)
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
            
            pages = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1250, chunk_overlap=250)
            chunks = []

            for i, page in enumerate(pages):
                texts = splitter.split_text(page.page_content)
                for j, text in enumerate(texts):
                    chunks.append(Document(
                        page_content=text,
                        metadata={
                            "id": str(uuid.uuid4()),
                            "file_name": path,
                            "page_num": i,
                            "chunk_idx": j,
                            "doc_type" : doc_type,
                            "embedding" : self.embeddings.embed_query(text)
                        }
                    ))
            return chunks
            
        def process_files_in_folders(self,base_folder):
            import os  
            chunks = []
            print("process_files_in_folders")
            count = -1
        
            for root, dirs, files in os.walk(base_folder):
                count += 1
        
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file_path)[1].lower()
        
                    if ext in [".pdf", ".docx"]:
                        try:
                            current_dir = os.path.dirname(os.path.abspath(file_path))

                            parent_dir = os.path.dirname(current_dir)

                            grandparent_dir = os.path.dirname(parent_dir)
        
                            
                            split_path = parent_dir.split(os.sep)
                            next_folder_name = None
                            if "hs_rag" in split_path:
                                hs_rag_index = split_path.index("hs_rag")
                                if hs_rag_index + 1 < len(split_path):
                                    next_folder_name = split_path[hs_rag_index + 1]
                                    print("this "+ next_folder_name)
                            file_chunks = self.get_chunk_of_file(file_path, next_folder_name)
                            chunks.extend(file_chunks)
        
                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")
        
            return chunks
            
        def delete_folder(self,folder_path):
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                    print(f"Klasor basariyla silindi: {folder_path}")
                except Exception as e:
                    print(f"Klasor silinirken bir hata olustu: {e}")
            else:
                print(f"Klasor bulunamadi: {folder_path}")
            

        def create_chunks(self,hukuk_dosya_no):
            data_loader = Pipeline.DataLoader()
            self.delete_folder("hs_rag")
            data_loader.extract_sbm_files_last(hukuk_dosya_no)
            chunks = self.process_files_in_folders("hs_rag")
            return chunks


        def read_eksper_pdf(self, path):
            loader = PyPDFLoader(path)
            docs = loader.load()
            rapor = ""
            for doc in docs:
                rapor += doc.page_content
            return rapor
        
        def get_hs_table(self,hukuk_dosya_no):
            loader = Pipeline.DataLoader()
            hs_table = loader.get_data_from_hs(hukuk_dosya_no)
            hs_table= json.loads(hs_table)
            hasar_dosya_no = hs_table[0]["HASAR_DOSYA_NO"]

            if self.eksper_already_exist(hukuk_dosya_no=hukuk_dosya_no):
                rapor_result = self.eksper_get_data(hukuk_dosya_no=hukuk_dosya_no)
                #GET FROM ELASTIC
            else:
                file_name = loader.download_evrak_as_pdf_eksper(loader.get_evrak_id_eksper(hasar_dosya_no), "eksper_dosyalari")
                if file_name == "asd":
                    return hs_table,"EKSPER DOES NOT EXISTS"
                rapor_result = self.read_eksper_pdf("eksper_dosyalari/{}".format(file_name))
                self.eksper_load_data(rapor_result,hukuk_dosya_no)

            return hs_table, rapor_result

    class Prompt():
        def __init__(self):
            self.system_prompt = """You are a Turkish talking law knowing insurer, you will response in only Turkish. Respond to the human as helpfully, Turkish(Turkce) and accurately as possible. You have access to the following tools: {tools}
            Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input). 
            Valid "action" values: "Final Answer" or {tool_names} . If returnet data is None say "Bu konuyla ilgili bi evraga erisemedim".
            For each question you have to pick ONLY one tool, pick it correctly. After selecting correct tool you will give the output using it. When you're done, complete with the line: END_OF_OUTPUT
            Provide only ONE action per $JSON_BLOB, as shown:"
            ```
            {{
            "action": $TOOL_NAME,
            "action_input": $INPUT
            }}
            ```
            Follow this format:
            Question: input question to answer
            Thought: consider previous and subsequent steps and all memory
            Action:
            ```
            $JSON_BLOB
            ```
            Observation: action result
            ... (repeat Thought/Action/Observation N times)
            Thought: I know what to respond
            Action:
            ```
            {{
            "action": "Final Answer",
            "action_input": "Final response to human"
            }}
            Begin! Reminder to ALWAYS respond with a valid json blob of a single action.
            Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation"""


            self.human_prompt = """{input}
            {agent_scratchpad}
            (reminder to always respond in a JSON blob)"""
        def create_prompt(self,tools):
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", self.human_prompt),
                ]
            )

            prompt = prompt.partial(
                tools=render_text_description_and_args(list(tools)),
                tool_names=", ".join([t.name for t in tools]),
            )
            return prompt
        



    class Agent():
        def __init__(self):
            self.embedding_model_id ="intfloat/multilingual-e5-large" #"sentence-transformers/all-minilm-l6-v2"
            self.model_id = "meta-llama/llama-3-3-70b-instruct"
            self.url= "https://cpd-ibm-cpd-instance.apps.ocpai.turkiyesigorta.com.tr/"
            self.api_key = "ljjOHUaNoxjrok6d2zIGPQhmYG8VKfMOFHlT0hmy"
            self.space_id = "3e3b6b9a-7812-4a30-9fcf-19de30f4f3de"
            self.project_id = "2ed5840f-2433-4d29-9fa9-3f2e0613a558"
            self.instance_id= "openshift"
            self.username  ="cpadmin"
            self.password = "swYO11qODwlhffktd55R0qtbDPfjO7Xn"
            self.user_memories = {}
            self.es = Elasticsearch("http://10.20.21.237:9200")
            self.base_index = "base_index_test6" #"base_index_test5"
            self.base_template =  "Answer the given questions using the retrieved context list. Only use the given informations. Your answer must be in Turkish. The question : {question} . Information Base : {chunks}"
            self.hukuk_dosya_no_index = "hukuk_dosya_no_index_test2"#"hukuk_dosya_no_index_test1"

            self.create_index_if_not_exists()

            try:
                # Check if the Elasticsearch cluster is reachable
                health = self.es.cluster.health()
                print("Elasticsearch cluster health:", health)
                
                if health['status'] == 'red':
                    print("Cluster health is RED! You might have issues with Elasticsearch nodes.")
                elif health['status'] == 'yellow':
                    print("Cluster health is YELLOW. Some replicas might not be allocated.")
                else:
                    print("Cluster health is GREEN. Everything seems fine.")

            except ConnectionError as e:
                print(f"Connection error: {e}")
            except TimeoutError as e:
                print(f"Timeout error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
            self.set_models()
            self.create_base_pipe
            self.set_tools_and_prompts( [
    "data/1.5.6098.pdf",
    "data/17hd-2015-11245.pdf",
    "data/17hd-2015-14700.pdf",
    "data/3. sahis mm.pdf",
    "data/4hd-2021-12519.pdf",
    "data/4hd-2021-5315.pdf",
    "data/4hd-2021-8670.pdf",
    "data/AFET SIGORTALARI KANUNU.pdf",
    "data/DASK calisma esaslari yon..pdf",
    "data/Daini Murtehin.pdf",
    "data/GENEL HUKUK.pdf",
    "data/GUVENCE HESABI YONETMELIGI.pdf",
    "data/GeneratePdf.pdf",
    "data/IKINCIL ONEMLI GENEL SARTLAR.pdf",
    "data/KDV HARIC %60 ORANINDA KISMI HASAR HALINDE PERT.pdf",
    "data/Karayolu Yolcu Tasimaciligi Zorunlu Koltuk Ferdi Kaza Sigortasi Genel Sartlari.pdf",
    "data/Kiymet kazanma tenzili.pdf",
    "data/MUTABAKATNAME - IHTIRAZI KAYIT.pdf",
    "data/Mesleki Sorumluluk Sigortasi Genel Sartlari.pdf",
    "data/SIGORTA BIRINCIL MEVZUAT.pdf",
    "data/SIGORTA YONETMELIK VE ONEMLI GENEL SARTLAR.pdf",
    "data/SIGORTACILIKTA TAHKIME ILISKIN YONETMELIK.pdf",
    "data/ZMMS genel sartlar.pdf",
    "data/acente yonetmelik.pdf",
    "data/bilgilendirme yonetmeligi.pdf",
    "data/broker yonetmelik.pdf",
    "data/ferdi kaza.pdf",
    "data/hukuksal koruma genel sartlar.pdf",
    "data/iSKONTO ALEYHE KARAR.pdf",
    "data/kasko genel sartlar.pdf",
    "data/medeni usul.pdf",
    "data/motorlu tasit imm.pdf",
    "data/sigortacilik kanunu.pdf",
    "data/tibbi kotu uygulama.pdf",
    "data/ttk 6. kitap.pdf",
    "data/zds talimat tebligi degisiklik.pdf",
    "data/zds talimat tebligi.pdf",
    "data/zorunlu deprem.pdf"
] )
        def create_index_if_not_exists(self):
            # Define custom mappings (optional, you can adjust them as needed)
            mappings_hukuk = {
                "properties": {
                    "hukuk_dosya_no": {"type": "keyword"},  # For exact match queries
                    "id": {"type": "keyword"},
                    "file_name": {"type": "text"},
                    "page_num": {"type": "integer"},
                    "chunk_idx": {"type": "integer"},
                    "page_content": {"type": "text"},
                    "doc_type": {"type": "keyword"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 1024,
                        "index": True,
                        "similarity" : "cosine"  # Adjust to your actual embedding dimension
                    }
                }
            }

            # Check if the index exists
            if not self.es.indices.exists(index=self.hukuk_dosya_no_index):
                # Create the index with the specified mappings
                self.es.indices.create(index=self.hukuk_dosya_no_index, body={
                    "mappings": mappings_hukuk
                })
                
                print(f"Index '{self.hukuk_dosya_no_index}' created.")
            else:
                print(f"Index '{self.hukuk_dosya_no_index}' already exists.")


        def set_models(self):
            credentials = {
                "url": self.url,
                "apikey": self.api_key
            }

            #project_id = project_id

            self.llm = WatsonxLLM(
                model_id=self.model_id,
                url=self.url,
                params={
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.TEMPERATURE: 0,
                    GenParams.MIN_NEW_TOKENS: 5,
                    GenParams.MAX_NEW_TOKENS: 8192,
                    GenParams.STOP_SEQUENCES: ["Human:", "Observation","END_OF_OUTPUT"],
                },
                project_id=self.project_id,
                username=self.username,
                password=self.password,
                space_id=self.space_id,
                instance_id=self.instance_id,
            # version="5.1.2"
            )



            self.embeddings = WatsonxEmbeddings(
                model_id=self.embedding_model_id,
                url=credentials["url"],
                apikey=self.api_key,
                project_id=self.project_id,
                username=self.username,
                password=self.password,
                instance_id= self.instance_id
            )

        def create_base_pipe(self):

            prompt = PromptTemplate.from_template(self.template)
            self.llm_chain = prompt | self.llm

        def hukuk_dosya_no_exists(self,hukuk_dosya_no):
            try:
                response = self.es.search(index=self.hukuk_dosya_no_index, body={
                    "query": {
                                "match": {
                            "hukuk_dosya_no": hukuk_dosya_no
                        }  # This matches all documents in the index
                    },
            "size": 1
                })

                return response["hits"]["total"]["value"] > 0

            except Exception as e:
                print(f"[ERROR] Failed to query Elasticsearch: {e}")
                return False
                
        def store_retrieved_docs(self,chunks, hukuk_dosya_no):
            # Check if any document with this hukuk_dosya_no already exists
            existing = self.es.search(index=self.hukuk_dosya_no_index, query={
                "term": { "hukuk_dosya_no": hukuk_dosya_no }
            })

            if existing["hits"]["total"]["value"] > 0:
                print(f"Document with hukuk_dosya_no '{hukuk_dosya_no}' already exists. Skipping.")
                return

            # Otherwise, store new documents
            for doc in chunks:
                self.es.index(index=self.hukuk_dosya_no_index, document={
                    "hukuk_dosya_no": hukuk_dosya_no,
                            "id": doc.metadata["id"],
                            "file_name": doc.metadata["id"],
                            "page_num": doc.metadata["page_num"],
                            "chunk_idx": doc.metadata["chunk_idx"],
                            "page_content" : doc.page_content,
                            "doc_type" : doc.metadata["doc_type"],
                            "embedding" : doc.metadata["embedding"]

                })


        def retrieve_from_db_for_dosya(self,question, hukuk_dosya_no:str, all_doc_types,top_k = 8):
            """
            Retrieves top documents related to a question from FAISS, using chunks
            matched by hukuk_dosya_no from Elasticsearch. Filters by doc_type.
            """
            #from elasticsearch import Elasticsearch
            # es = Elasticsearch("http://localhost:9200")
            #index_name = "agent_retrieval"

            retrieved_docs = []
            for doc_type in all_doc_types:
                # Construct the vector-based search query with a filter on doc_type
                response = self.es.search(
                    index=self.hukuk_dosya_no_index,
                    size=top_k,  # top 8 results per doc_type
                            query={
            "script_score": {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"hukuk_dosya_no": hukuk_dosya_no}},
                            {"term": {"doc_type": doc_type}}  # adjust field name if needed
                        ]
                    }
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {
                        "query_vector": self.embeddings.embed_query(question)
                    }
                }
            }
        }
    )
                 #   query={
                 #       "script_score": {
                 #           "query": {
                   #             "match": {
                   #             "hukuk_dosya_no": hukuk_dosya_no
                    #        }  # This matches all documents in the index
                    #    },
                     #       "script": {
                     #           "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    #            "params": {
                #                    "query_vector": self.embeddings.embed_query(question)
                  #              }
               #             }
                #        }
              #      }
              #  )

                #print(f"Results for doc_type: {doc_type}")
                for hit in response["hits"]["hits"]:
                    doc = hit["_source"]
                    score = hit["_score"]
                   # print(f"Score: {score}, Page: {doc['page_num']}, Chunk: {doc['chunk_idx']}")
                   # print(f"Content: {doc['page_content'][:200]}...\n")
                    retrieved_docs.append(doc["page_content"])

            print("length:"+str(len(retrieved_docs)))
            return retrieved_docs




        def get_memory_for_user(self,user_id):  
            if user_id not in self.user_memories:  
                self.user_memories[user_id] = ConversationBufferMemory(  
                    memory_key="chat_history", return_messages=True  
                )  
            return self.user_memories[user_id]  

        def set_tools_and_prompts(self,base_pdfs):
            self.base_model_retriver = Pipeline.BaseRetrival()
            #self.base_model_retriver.run(base_pdfs)  #EDIT THIS FOR MEVZUAT

            @tool
            def get_dilekce_context(question: str):
                """This is your main knowledge base. If user asks a generic question about some document without spesific dosya number use this."""


                response = self.es.search(
                index=self.base_index,
                size=8,
                query={
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {
                                "query_vector": self.embeddings.embed_query(question)
                            }
                        }
                    }
                }
                )

                # Extract and display results
                retrieved_chunks = []
                for hit in response["hits"]["hits"]:
                    doc = hit["_source"]
                    score = hit["_score"]
                  #  print(f"Score: {score}, Page: {doc['page_num']}, Chunk: {doc['chunk_idx']}")
                   # print(f"Content: {doc['page_content'][:200]}...\n")
                    retrieved_chunks.append(doc["page_content"])

                #retrieved elemanlari hazir

               # prompt = PromptTemplate.from_template(self.base_template)
               # self.llm_chain = prompt | self.llm
            
               # response = self.llm_chain.invoke({
                #    "question": question,
               #     "chunks": retrieved_chunks
               # })

                return retrieved_chunks
                
            @tool    
            def daily_question_answering_and_check_memory(question:str):
                """Use this tool when a daily question asked to you. Like greetings or non document based general knowledge."""

                return self.memory, question
            @tool
            def summary_for_hukuk_dosya_number(doc_type:str,question:str,hukuk_dosya_no:str):
                """Use this tool when user asks for the summary of spesific document name for a spesific hukuk dosya number.
                The document name (doc_type) can be one of these : Cevap Dilekcesi , Basvuru Dilekcesi , Ekspertiz Raporu , Bilirkisi Raporu , Karar Dokumani ."""
                hukukretrive= Pipeline.HukukRetrival()
                if doc_type == "Ekspertiz Raporu":
                    tables , eksper_raporu = hukukretrive.get_hs_table(hukuk_dosya_no)
                    return eksper_raporu
                if self.hukuk_dosya_no_exists(hukuk_dosya_no):
                    if doc_type == "Cevap Dilekcesi":
                        retrieved_docs = self.retrieve_from_db_for_dosya(question, hukuk_dosya_no, ["Sigorta Sirket Cevaplari"],top_k = 500)
                        
                        return retrieved_docs
                    if doc_type == "Basvuru Dilekcesi":
                        retrieved_docs = self.retrieve_from_db_for_dosya(question, hukuk_dosya_no, ["Basvuru Dokumanlari"],top_k = 500)
                        return retrieved_docs
                    if doc_type == "Bilirkisi Raporu":
                        retrieved_docs = self.retrieve_from_db_for_dosya(question, hukuk_dosya_no, ["Uyusmazlik Bilirkisi Raporu"],top_k = 500)
                        return retrieved_docs
                    if doc_type == "Karar Dokumani":
                        retrieved_docs = self.retrieve_from_db_for_dosya(question, hukuk_dosya_no, ["Hakemler Tarafindan E-imzali Yuklenen Kararlar"],top_k = 500)
                        print(retrieved_docs)
                        return retrieved_docs             
                else:
                    try:
                        self.hukuk_model_chunks = hukukretrive.create_chunks(hukuk_dosya_no)
                    except:
                        print("fail !")
                    print("chunkss hazir")
                    try:
                        self.store_retrieved_docs(self.hukuk_model_chunks, hukuk_dosya_no)
                    except:
                        print("store_retrived_docs failed")  

                    if doc_type == "Cevap Dilekcesi":
                        retrieved_docs = self.retrieve_from_db_for_dosya(question, hukuk_dosya_no, ["Sigorta Sirket Cevaplari"],top_k = 500)
                        return retrieved_docs
                    if doc_type == "Basvuru Dilekcesi":
                        retrieved_docs = self.retrieve_from_db_for_dosya(question, hukuk_dosya_no, ["Basvuru Dokumanlari"],top_k = 500)
                        return retrieved_docs
                    if doc_type == "Bilirkisi Raporu":
                        retrieved_docs = self.retrieve_from_db_for_dosya(question, hukuk_dosya_no, ["Uyusmazlik Bilirkisi Raporu"],top_k = 500)
                        return retrieved_docs
                    if doc_type == "Karar Dokumani":
                        retrieved_docs = self.retrieve_from_db_for_dosya(question, hukuk_dosya_no, ["Hakemler Tarafindan E-imzali Yuklenen Kararlar"],top_k = 500)
                        return retrieved_docs       

            @tool
            def hukuk_dosya_no_questions_without_summary(question:str,hukuk_dosya_no:str):
                """Use this when user asks a question about a spesific hukuk dosya number."""
                all_doc_types = ['Basvuru Dokumanlari' , 'Hakemler Tarafindan E-imzali Yuklenen Kararlar',  'Sigorta Sirket Cevaplari'  ,'Uyusmazlik Bilirkisi Raporu']  # Replace with your real types
                self.hukuk_model= Pipeline.HukukRetrival()
                tables , eksper_raporu = self.hukuk_model.get_hs_table(hukuk_dosya_no)
                if self.hukuk_dosya_no_exists(hukuk_dosya_no):
                    print("hukuk dosya no existe girdi dayi")

                    retrieved_docs = self.retrieve_from_db_for_dosya(question, hukuk_dosya_no, all_doc_types)
                    print("eksper--------------------------------------:")
                    print(len(eksper_raporu[:10]))
                    return  str(retrieved_docs) + "TABLOLAR :" + str(tables) + "EKSPER RAPORU :" + str(eksper_raporu)
                
                else:
                    print("a else girdi")

                    try:
                        self.hukuk_model_chunks = self.hukuk_model.create_chunks(hukuk_dosya_no)
                    except:
                        print("b")

                    print("chunkss hazir")

                    try:
                        self.store_retrieved_docs(self.hukuk_model_chunks, hukuk_dosya_no)
                    except:
                        print("store_retrived_docs failed")

                    """                    # Convert chunks to FAISS vector store instead of Chroma
                    self.hukuk_model_retriver = FAISS.from_documents(
                        documents=self.hukuk_model_chunks,
                        embedding=self.embeddings,
                    )"""

                    retrieved_docs = []
                    for doc_type in all_doc_types:
                        # Construct the vector-based search query with a filter on doc_type
                        response = self.es.search(
                            index=self.hukuk_dosya_no_index,
                            size=8,  # top 8 results per doc_type
                            query={
                                "script_score": {
                                    "query": {
                                        "bool": {
                                            "must": [
                                                {"match": {"hukuk_dosya_no": hukuk_dosya_no}},
                                                {"term": {"doc_type": doc_type}}  # adjust field name if needed
                                            ]
                                        }
                                    },
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                        "params": {
                                            "query_vector": self.embeddings.embed_query(question)
                                        }
                                    }
                                }
                            }
                        )

                        print(f"Results for doc_type: {doc_type}")
                        for hit in response["hits"]["hits"]:
                            doc = hit["_source"]
                            score = hit["_score"]
                          #  print(f"Score: {score}, Page: {doc['page_num']}, Chunk: {doc['chunk_idx']}")
                          # print(f"Content: {doc['page_content'][:200]}...\n")
                            retrieved_docs.append(doc["page_content"])

                    return str(retrieved_docs) + str(tables) + str(eksper_raporu)


   
            self.tools = [hukuk_dosya_no_questions_without_summary,daily_question_answering_and_check_memory,get_dilekce_context,summary_for_hukuk_dosya_number]   
            

            prompt_creator = Pipeline.Prompt()
            self.prompt = prompt_creator.create_prompt(tools=self.tools)

        def run_agent(self,input_data):  
            user_id = input_data["user_id"]  
            self.memory = self.get_memory_for_user(user_id)    
            # Only pass what the agent expects; 'input' is standard for OpenAI agents/prompts  
            chain_input = {  
                "input": input_data["input"]  
            }  
            chain = (  
                RunnablePassthrough.assign(  
                    agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),  
                )  
                | self.prompt  
                | self.llm  
                | JSONAgentOutputParser()  
            )  

            agent_executor = AgentExecutor(  
                agent=chain,  
                tools=self.tools,  
                memory=self.memory,  # <-- Attach memory here!  
                handle_parsing_errors=True,  
                verbose=True,  
            )  
        
            return agent_executor.invoke(chain_input)  # or any other agent_executor run method  
        
        """input_data = {  
        "user_id": "012",  
        "input" : "100321 Nolu dosyada davacinin adi nedir"  
    }"""



    async def on_startup(self):
        print(os.getcwd())
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    async def on_valves_updated(self):
        # This function is called when the valves are updated.
        pass

    async def inlet(self, body: dict, user: dict) -> dict:
        print(os.getcwd())
        return body
    
    async def outlet(self, body: dict, user: dict) -> dict:
        # This function is called after the OpenAI API response is completed. You can modify the messages after they are received from the OpenAI API.
        return body

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(os.getcwd())
        messages = body.get("messages", [])
        user_message = get_last_user_message(messages)
        user_id = "12312"
        global agent  # Allows modifying the global agent

        if agent is None:
            print("Agent not created yet  creating now.")
            agent = Pipeline.Agent()
        else:
            print("Agent already exists  reusing.")
        input_data={"user_id":user_id, "input":user_message}
        
        value = agent.run_agent(input_data=input_data)
        return value["output"]
