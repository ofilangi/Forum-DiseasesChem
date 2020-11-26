
import argparse, sys, os
import rdflib
import configparser
import subprocess

from Id_mapping import Id_mapping
from processing_functions import *

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
parser.add_argument("--version", help="version of the PMID-CID ressource, if none, the date is used")
args = parser.parse_args()

if not os.path.exists(args.config):
    print("Config file : " + args.config + " does not exist")
    sys.exit(3)

try:    
    config = configparser.ConfigParser()
    config.read(args.config)
except configparser.Error as e:
    print(e)
    sys.exit(3)

namespaces = {
    "cito": rdflib.Namespace("http://purl.org/spar/cito/"),
    "compound": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"),
    "reference": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/reference/"),
    "endpoint":	rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/"),
    "obo": rdflib.Namespace("http://purl.obolibrary.org/obo/"),
    "dcterms": rdflib.Namespace("http://purl.org/dc/terms/"),
    "fabio": rdflib.Namespace("http://purl.org/spar/fabio/"),
    "mesh": rdflib.Namespace("http://id.nlm.nih.gov/mesh/"),
    "void": rdflib.Namespace("http://rdfs.org/ns/void#"),
    "skos": rdflib.Namespace("http://www.w3.org/2004/02/skos/core#"),
    "owl": rdflib.Namespace("http://www.w3.org/2002/07/owl#")
}


# Global
path_to_dumps = args.out

# MetaNetX:
MetaNetX_v = args.version

path_to_g_MetaNetX = path_to_dumps + "MetaNetX/metanetx.ttl.gz"
uri_source_graph = config['METANETX'].get('uri')
# Intra
path_to_dir_Intra = config['INTRA'].get('path_to_dir_from_dumps')

uri_MetaNetX = base_uri_MetaNetX + MetaNetX_v
linked_grahs = [base_uri_Intra + MetaNetX_v]

update_f_name = "MetaNetX_update_file.sh"
with open(path_to_dumps + update_f_name, "w") as update_f:
    pass

print("Mapping MetaNetX v." + MetaNetX_v + " graph don't exist, create graph.")
# Intialyze Object:
map_ids = Id_mapping(MetaNetX_v, namespaces)
print("Import configuration table ...", end = '')
map_ids.import_table_infos(config['METANETX'].get('path_to_table_infos'))
# Import graph :
print("Ok\nTry to load MetanetX graph from " + config['METANETX'].get('g_path') + " ...", end = '')
graph_metaNetX = rdflib.Graph()
graph_metaNetX.parse(path_to_g_MetaNetX, format = "turtle")
print("Ok\nTry de create URIs equivalences from MetaNetX graph ...")
# Create graphs :
map_ids.create_graph_from_MetaNetX(graph_metaNetX, path_to_dumps + "Id_mapping/MetaNetX/", uri_source_graph)
map_ids.export_intra_eq(path_to_dumps + path_to_dir_Intra, "MetaNetX")

print("Try to load mapping graphs in Virtuoso ...")
create_update_file_from_ressource(path_to_dumps, "Id_mapping/MetaNetX/" + MetaNetX_v + "/", "*trig", '', update_f_name)
create_update_file_from_ressource(path_to_dumps, "Id_mapping/MetaNetX/" + MetaNetX_v + "/", "void.ttl", base_uri_MetaNetX + MetaNetX_v, update_f_name)

print("Try to intra mapping graphs in Virtuoso ...")
create_update_file_from_ressource(path_to_dumps, path_to_dir_Intra + "MetaNetX/" + MetaNetX_v + "/", "*trig", '', update_f_name)
create_update_file_from_ressource(path_to_dumps, path_to_dir_Intra + "MetaNetX/" + MetaNetX_v + "/", "void.ttl", base_uri_Intra + MetaNetX_v, update_f_name)